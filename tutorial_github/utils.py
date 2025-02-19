import logging
from typing import List, Optional, Tuple, Dict, Any

import os
from github import Github, Auth
from datetime import datetime
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
    github_name: Optional[List[str]], 
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Fetches the number of commits made in the specified repositories
    and by the specified GitHub users within a given period.

    :param github_name: List of GitHub usernames to filter commits. If None, fetches for all users.
    :param period: Start and end datetime tuple for filtering commits.
    :param repo_name: List of repository names to fetch commits from. If None, considers all repos.
    :return: A JSON object containing:
        - total_commits (int): Total number of commits.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

def get_total_prs(
    github_name: Optional[List[str]], 
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Fetches the number of pull requests made in the specified repositories
    and by the specified GitHub users within a given period.

    :param github_name: List of GitHub usernames to filter pull requests.
    :param period: Start and end datetime tuple for filtering pull requests.
    :param repo_name: List of repository names to fetch pull requests from.
    :return: A JSON object containing:
        - total_prs (int): Total number of pull requests.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

def get_prs_not_merged(
    github_name: Optional[List[str]], 
    period: Optional[Tuple[datetime, datetime]], 
    repo_name: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Fetches the count of closed but unmerged pull requests in the specified repositories
    and by the specified GitHub users within a given period.

    :param github_name: List of GitHub usernames to filter pull requests.
    :param period: Start and end datetime tuple for filtering pull requests.
    :param repo_name: List of repository names to fetch pull requests from.
    :return: A JSON object containing:
        - prs_not_merged (int): Total number of closed but unmerged pull requests.
        - period (str): The time range considered.
        - repositories (List[str]): List of repositories included.
    """
    pass

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
def get_repo_names(
    client: Github, org_or_user_name: str
) -> Dict[str, Any]:
    """
    Retrieve a list of repositories under a specific organization or user.

    :param client: An instance of the PyGithub client.
    :param org_or_user_name: Name of the GitHub organization or user.
    :return: A JSON object containing:
        - owner (str): Name of the organization or user.
        - repositories (List[str]): List of repository names.
    """
    try:
        # Attempt to get as an organization
        owner = client.get_organization(org_or_user_name)
    except:
        try:
            # If not an organization, attempt to get as a user
            owner = client.get_user(org_or_user_name)
        except:
            raise ValueError(f"'{org_or_user_name}' is neither a valid GitHub user nor organization.")

    repos = [repo.name for repo in owner.get_repos()]
    result = {"owner": org_or_user_name, "repositories": repos}
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