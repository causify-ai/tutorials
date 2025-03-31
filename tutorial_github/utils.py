import logging
from typing import List, Optional, Tuple, Dict, Any

import os
from github import Github, Auth
from datetime import datetime, timezone
from tqdm import tqdm
# import helpers.hdbg as hdbg

_LOG = logging.getLogger(__name__)

# #############################################################################
# GitHub API Setup
# #############################################################################

class GitHubAPI:
    """
    A class to initialize and manage authentication with the GitHub API using PyGithub.
    """

    def __init__(self, access_token: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initializes the GitHub API client.

        :param access_token: GitHub Personal Access Token. If not provided,
                             it is fetched from the environment variable `GITHUB_ACCESS_TOKEN`.
        :param base_url: Optional custom GitHub Enterprise base URL.
        """
        self.access_token = access_token or os.getenv("GITHUB_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("GitHub Access Token is required. Set it as an environment variable or pass it explicitly.")
        
        auth = Auth.Token(self.access_token)
        self.github = Github(base_url=base_url, auth=auth) if base_url else Github(auth=auth)
    
    def get_client(self) -> Github:
        """
        Returns the authenticated GitHub client.

        :return: An instance of the authenticated PyGithub client.
        """
        return self.github
    
    def close_connection(self):
        """
        Closes the GitHub API connection.
        """
        self.github.close()

# #############################################################################
# Global Metrics APIs
# #############################################################################

def get_total_commits(
    client: Github,
    org_name: str,
    github_names: Optional[List[str]] = None,
    period: Optional[Tuple[datetime, datetime]] = None
) -> Dict[str, Any]:
    """
    Fetches the number of commits made in the repositories of the specified
    organization, optionally filtered by GitHub usernames and a
    specified time period.

    :param client: Authenticated instance of the PyGithub client.
    :param org_name: Name of the GitHub organization.
    :param github_names: List of GitHub usernames to filter commits. If None, fetches for all users.
    :param period: Tuple containing start and end datetime for filtering commits.
    :return: A dictionary containing:
        - total_commits (int): Total number of commits across all repositories.
        - period (str): The time range considered.
        - commits_per_repository (Dict[str, int]): Dictionary with repository names as keys and commit counts as values.
    """
    try:
        # Retrieve repositories for the specified organization
        repos_info = get_repo_names(client, org_name)
        repositories = repos_info.get("repositories", [])
    except Exception as e:
        _LOG.error(f"Error retrieving repositories for '{org_name}': {e}")
        return {"total_commits": 0, "period": "N/A", "commits_per_repository": {}}

    total_commits = 0
    commits_per_repository = {}
    since, until = period if period else (None, None)

    # Iterate over each repository
    for repo_name in repositories:
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_commit_count = 0
            if github_names:
                for username in github_names:
                    commits = repo.get_commits(author=username, since=since, until=until)
                    repo_commit_count += commits.totalCount
            else:
                commits = repo.get_commits(since=since, until=until)
                repo_commit_count = commits.totalCount

            commits_per_repository[repo_name] = repo_commit_count
            total_commits += repo_commit_count
        except Exception as e:
            _LOG.error(f"Error accessing commits for repository '{repo_name}': {e}")
            commits_per_repository[repo_name] = 0

    result = {
        "total_commits": total_commits,
        "period": f"{since} to {until}" if since and until else "All time",
        "commits_per_repository": commits_per_repository
    }

    return result

def get_total_prs(
    client: Github,
    org_name: str,
    github_names: Optional[List[str]] = None,
    period: Optional[Tuple[datetime, datetime]] = None,
    state: str = 'open'
) -> Dict[str, Any]:
    """
    Fetches the number of pull requests made in the repositories of the specified
    organization, optionally filtered by GitHub usernames, a specified time period,
    and the state of the pull requests.

    :param client: Authenticated instance of the PyGithub client.
    :param org_name: Name of the GitHub organization.
    :param github_names: List of GitHub usernames to filter pull requests. If None, fetches for all users.
    :param period: Tuple containing start and end datetime for filtering pull requests.
    :param state: The state of the pull requests to fetch. Can be 'open', 'closed', or 'all'.
    :return: A dictionary containing:
        - total_prs (int): Total number of pull requests.
        - period (str): The time range considered.
        - prs_per_repository (Dict[str, int]): Dictionary with repository names as keys and pull request counts as values.
    """
    try:
        # Retrieve repositories for the specified organization
        repos_info = get_repo_names(client, org_name)
        repositories = repos_info.get("repositories", [])
    except Exception as e:
        _LOG.error(f"Error retrieving repositories for '{org_name}': {e}")
        return {"total_prs": 0, "period": "N/A", "prs_per_repository": {}}

    total_prs = 0
    prs_per_repository = {}

    # Define the date range and ensure they are timezone-aware in UTC
    if period:
        since, until = [dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc) for dt in period]
    else:
        since = until = None

    # Iterate over each repository with progress tracking
    for repo_name in tqdm(repositories, desc="Processing repositories", unit="repo"):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_pr_count = 0
            pulls = repo.get_pulls(state=state)  # Fetch pull requests based on the specified state

            for pr in pulls:
                # Ensure pr.created_at is timezone-aware in UTC
                pr_created_at = pr.created_at.replace(tzinfo=timezone.utc) if pr.created_at.tzinfo is None else pr.created_at.astimezone(timezone.utc)
                # Filter by creation date if period is specified
                if since and until and not (since <= pr_created_at <= until):
                    continue
                # Filter by author if github_names is specified
                if github_names and pr.user.login not in github_names:
                    continue
                repo_pr_count += 1

            prs_per_repository[repo_name] = repo_pr_count
            total_prs += repo_pr_count
        except Exception as e:
            _LOG.error(f"Error accessing pull requests for repository '{repo_name}': {e}")
            prs_per_repository[repo_name] = 0

    result = {
        "total_prs": total_prs,
        "period": f"{since} to {until}" if since and until else "All time",
        "prs_per_repository": prs_per_repository
    }

    return result

def get_prs_not_merged(
    client: Github,
    org_name: str,
    github_names: Optional[List[str]] = None,
    period: Optional[Tuple[datetime, datetime]] = None
) -> Dict[str, Any]:
    """
    Fetches the count of closed but unmerged pull requests in the specified repositories
    and by the specified GitHub users within a given period.

    :param client: Authenticated instance of the PyGithub client.
    :param org_name: Name of the GitHub organization.
    :param github_names: List of GitHub usernames to filter pull requests. If None, fetches for all users.
    :param period: Tuple containing start and end datetime for filtering pull requests.
    :return: A dictionary containing:
        - prs_not_merged (int): Total number of closed but unmerged pull requests.
        - period (str): The time range considered.
        - prs_per_repository (Dict[str, int]): Dictionary with repository names as keys and unmerged pull request counts as values.
    """
    try:
        # Retrieve repositories for the specified organization
        repos_info = get_repo_names(client, org_name)
        repositories = repos_info.get("repositories", [])
    except Exception as e:
        _LOG.error(f"Error retrieving repositories for '{org_name}': {e}")
        return {"prs_not_merged": 0, "period": "N/A", "prs_per_repository": {}}

    total_unmerged_prs = 0
    prs_per_repository = {}

    # Define the date range and ensure they are timezone-aware in UTC
    if period:
        since, until = [dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc) for dt in period]
    else:
        since = until = None

    # Iterate over each repository with progress tracking
    for repo_name in tqdm(repositories, desc="Processing repositories", unit="repo"):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_unmerged_pr_count = 0
            pulls = repo.get_pulls(state='closed')  # Fetch closed pull requests

            for pr in pulls:
                try:
                    # Print progress
                    # _LOG.info(f"Processing PR #{pr.number} from {repo_name}")

                    # Ensure pr.created_at is always set before usage
                    pr_created_at = pr.created_at if pr.created_at else datetime.min
                    if pr_created_at.tzinfo is None:
                        pr_created_at = pr_created_at.replace(tzinfo=timezone.utc)
                    else:
                        pr_created_at = pr_created_at.astimezone(timezone.utc)

                    # Filter by unmerged status
                    if pr.merged:
                        continue
                    # Filter by author if github_names is specified
                    if github_names and pr.user.login not in github_names:
                        continue
                    # Filter by creation date if period is specified
                    if since and until and not (since <= pr_created_at <= until):
                        continue

                    repo_unmerged_pr_count += 1

                except Exception as e:
                    _LOG.error(f"Error processing PR #{pr.number} in '{repo_name}': {e}")
                    continue  # Skip this PR and proceed with the next one

            prs_per_repository[repo_name] = repo_unmerged_pr_count
            total_unmerged_prs += repo_unmerged_pr_count
        except Exception as e:
            _LOG.error(f"Error accessing pull requests for repository '{repo_name}': {e}")
            prs_per_repository[repo_name] = 0

    result = {
        "prs_not_merged": total_unmerged_prs,
        "period": f"{since} to {until}" if since and until else "All time",
        "prs_per_repository": prs_per_repository
    }

    return result

def get_issues_without_assignee(
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Retrieve the number of issues without an assignee within a specified time range.

    :param period: Start and end datetime tuple for filtering issues.
    :param repo_name: List of repository names to fetch issues from.
    :return: A JSON object containing:
        - issues_without_assignee (int): Total number of issues without an assignee.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

# #############################################################################
# Individual User Metrics APIs
# #############################################################################

def get_commits_by_person(
    github_name: str, 
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Retrieve the number of commits made by a specific GitHub user.

    :param github_name: GitHub username to fetch commit data for.
    :param period: Start and end datetime tuple for filtering commits.
    :param repo_name: List of repository names to fetch commits from.
    :return: A JSON object containing:
        - user (str): GitHub username.
        - total_commits (int): Total number of commits.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

def get_prs_by_person(
    github_name: str, 
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Fetches the number of pull requests created by a specific GitHub user in given repositories and period.

    :param github_name: GitHub username to fetch pull request data for.
    :param period: Start and end datetime tuple for filtering pull requests.
    :param repo_name: List of repository names to fetch pull requests from.
    :return: A JSON object containing:
        - user (str): GitHub username.
        - total_prs (int): Total number of pull requests created.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

def get_prs_not_merged_by_person(
    github_name: str, 
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Fetches the number of pull requests created by a specific GitHub user that are closed but not merged.

    :param github_name: GitHub username to fetch pull request data for.
    :param period: Start and end datetime tuple for filtering pull requests.
    :param repo_name: List of repository names to fetch pull requests from.
    :return: A JSON object containing:
        - user (str): GitHub username.
        - prs_not_merged (int): Total number of closed but unmerged pull requests.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

# #############################################################################
# Utility APIs
# #############################################################################

# TODO(prahar08modi): Test the function using pytest
def get_repo_names(client: Github, org_name: str) -> Dict[str, List[str]]:
    """
    Retrieve a list of repositories under a specific organization.

    :param client: An instance of the PyGithub client.
    :param org_name: Name of the GitHub organization.
    :return: A dictionary containing:
        - owner (str): Name of the organization.
        - repositories (List[str]): List of repository names.
    """
    try:
        # Attempt to get the organization
        owner = client.get_organization(org_name)
    except Exception as e:
        _LOG.error(f"Error retrieving organization '{org_name}': {e}")
        raise ValueError(f"'{org_name}' is not a valid GitHub organization.")

    repos = [repo.name for repo in owner.get_repos()]
    result = {"owner": org_name, "repositories": repos}
    return result

# TODO(prahar08modi): Test the function using pytest
def get_github_contributors(
    client: Github, repo_names: List[str]
) -> Dict[str, List[str]]:
    """
    Retrieves GitHub usernames contributing to specified repositories.

    :param client: An instance of the PyGithub client.
    :param repo_names: List of repository names in the format 'owner/repo' to fetch contributor usernames.
    :return: A dictionary containing:
        - repository (str): Repository name.
        - contributors (List[str]): List of contributor GitHub usernames.
    """
    result = {}
    for repo_name in repo_names:
        try:
            repo = client.get_repo(repo_name)
            contributors = [contributor.login for contributor in repo.get_contributors()]
            result[repo_name] = contributors
        except Exception as e:
            _LOG.error(f"Error fetching contributors for {repo_name}: {e}")
            result[repo_name] = []
    return result