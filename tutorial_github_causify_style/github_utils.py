import datetime
import logging
import os
import time
from datetime import timezone
from typing import Any, Dict, List, Optional, Tuple

import github
import pandas as pd
from tqdm import tqdm

_LOG = logging.getLogger(__name__)


# #############################################################################
# GitHubAPI
# #############################################################################


class GitHubAPI:
    """
    A class to initialize and manage authentication with the GitHub API using
    PyGithub.
    """

    def __init__(
        self, access_token: Optional[str] = None, base_url: Optional[str] = None
    ):
        """
        Initialize the GitHub API client.

        :param access_token: github personal access token; if not provided, it
            is fetched from the environment variable `GITHUB_ACCESS_TOKEN`
        :param base_url: optional custom GitHub Enterprise base URL
        """
        self.access_token = access_token or os.getenv("GITHUB_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "GitHub Access Token is required. Set it as an environment variable or pass it explicitly."
            )
        auth = github.Auth.Token(self.access_token)
        self.github = (
            github.Github(base_url=base_url, auth=auth)
            if base_url
            else github.Github(auth=auth)
        )

    def get_client(self) -> github.Github:
        """
        Return the authenticated GitHub client.

        :return: an instance of the authenticated PyGithub client
        """
        return self.github

    def close_connection(self) -> None:
        """
        Close the GitHub API connection.
        """
        self.github.close()


# #############################################################################
# Utility APIs
# #############################################################################


def get_repo_names(client: github.Github, org_name: str) -> Dict[str, List[str]]:
    """
    Retrieve a list of repositories under a specific organization.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :return: a dictionary containing:
        - owner: name of the organization
        - repositories: repository names
    """
    try:
        # Attempt to get the organization.
        owner = client.get_organization(org_name)
    except Exception as e:
        _LOG.error("Error retrieving organization '%s': %s", org_name, e)
        raise ValueError(
            f"'{org_name}' is not a valid GitHub organization."
        ) from e
    repos = [repo.name for repo in owner.get_repos()]
    result = {"owner": org_name, "repositories": repos}
    return result


def get_github_contributors(
    client: github.Github, repo_names: List[str]
) -> Dict[str, List[str]]:
    """
    Retrieve GitHub usernames contributing to specified repositories.

    :param client: authenticated instance of the PyGithub client
    :param repo_names: repository names in the format 'owner/repo' to fetch
        contributor usernames
    :return: a dictionary containing:
        - repository: repository name
        - contributors: contributor GitHub usernames
    """
    result = {}
    for repo_name in repo_names:
        try:
            repo = client.get_repo(repo_name)
            contributors = [
                contributor.login for contributor in repo.get_contributors()
            ]
            result[repo_name] = contributors
        except Exception as e:
            _LOG.error("Error fetching contributors for %s: %s", repo_name, e)
            result[repo_name] = []
    return result


def normalize_period_to_utc(
    period: Optional[Tuple[datetime.datetime, datetime.datetime]],
) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
    """
    Convert a datetime period to UTC and ensure both dates are timezone-aware.

    :param period: start and end datetime
    :return: tuple of UTC-aware start and end datetime, or (None, None)
        if period is None
    """
    if not period:
        return None, None
    return tuple(
        (
            dt.replace(tzinfo=datetime.timezone.utc)
            if dt.tzinfo is None
            else dt.astimezone(datetime.timezone.utc)
        )
        for dt in period
    )


def wait_for_rate_limit_reset(client: github.Github):
    """
    Wait until the Github rate limit resets.

    :param client: authenticated instance of the PyGithub client
    """
    rate_limit = client.get_rate_limit()
    remaining = rate_limit.core.remaining
    reset_timestamp = rate_limit.core.reset.timestamp()
    current_timestamp = datetime.datetime.now(timezone.utc).timestamp()
    if remaining == 0:
        sleep_time = reset_timestamp - current_timestamp
        if sleep_time > 0:
            print(f"[Rate Limit Hit] Sleeping for {sleep_time/60:.2f} minutes...")
            time.sleep(sleep_time + 5)


# #############################################################################
# Global Metrics APIs
# #############################################################################


def get_total_commits(
    client: github.Github,
    org_name: str,
    usernames: Optional[List[str]] = None,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    repo_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch the number of commits made in the repositories of the specified
    organization, optionally filtered by GitHub usernames and a specified time
    period.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :param usernames: GitHub usernames to filter commits; if None, fetches for
        all users
    :param period: start and end datetime for filtering commits
    :param repo_names: repository names to fetch commits from; if None, fetches
        from all repositories in the organization
    :return: a dictionary containing:
        - total_commits (int): total number of commits across all repositories
        - period (str): the time range considered
        - commits_per_repository (Dict[str, Any]): repository
            names mapped to branch names mapped to commit, addition, deletion, and
            total change counts
    """
    try:
        if not repo_names:
            # Retrieve repositories for the specified organization.
            repos_info = get_repo_names(client, org_name)
            repositories = repos_info.get("repositories", [])
        else:
            repositories = repo_names
    except Exception as e:
        _LOG.error("Error retrieving repositories for '%s': %s", org_name, e)
        return {
            "total_commits": 0,
            "period": "N/A",
            "commits_per_repository": {},
        }
    total_commits = 0
    commits_per_repository = {}
    since, until = period if period else (None, None)
    # Iterate over each repository.
    for repo_name in tqdm(
        repositories, desc="Processing repositories", unit="repo"
    ):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            branch_commit_counts = {}
            for branch in repo.get_branches():
                branch_commit_count = 0
                branch_additions = 0
                branch_deletions = 0
                if usernames:
                    for username in usernames:
                        commits = repo.get_commits(
                            sha=branch.name,
                            author=username,
                            since=since,
                            until=until,
                        )
                        for commit in commits:
                            if commit.stats:
                                branch_commit_count += 1
                                branch_additions += commit.stats.additions
                                branch_deletions += commit.stats.deletions
                else:
                    commits = repo.get_commits(
                        sha=branch.name, since=since, until=until
                    )
                    for commit in commits:
                        if commit.stats:
                            branch_commit_count += 1
                            branch_additions += commit.stats.additions
                            branch_deletions += commit.stats.deletions
                if branch_commit_count > 0:
                    branch_commit_counts[branch.name] = {
                        "commits": branch_commit_count,
                        "additions": branch_additions,
                        "deletions": branch_deletions,
                        "total_changes": branch_additions + branch_deletions,
                    }
                    total_commits += branch_commit_count
                if branch_commit_counts:
                    commits_per_repository[repo_name] = branch_commit_counts
        except Exception as e:
            _LOG.error(
                "Error accessing commits for repository '%s': %s", repo_name, e
            )

    return {
        "total_commits": total_commits,
        "period": f"{since} to {until}" if since and until else "All time",
        "commits_per_repository": commits_per_repository,
    }


def get_total_prs(
    client: github.Github,
    org_name: str,
    usernames: Optional[List[str]] = None,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    state: str = "open",
    repo_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch the number of pull requests made in the repositories of the specified
    organization, optionally filtered by GitHub usernames, a specified time
    period, and the state of the pull requests.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :param usernames: GitHub usernames to filter pull requests; if None, fetches
        for all users
    :param period: start and end datetime for filtering pull requests
    :param state: the state of the pull requests to fetch; can be 'open', 'closed', or 'all'
    :param repo_names: repository names to fetch PRs from; if None, fetches
        from all repositories in the organization
    :return: a dictionary containing:
        - total_prs (int): total number of pull requests
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and pull
            request counts as values
    """
    try:
        if not repo_names:
            # Retrieve repositories for the specified organization.
            repos_info = get_repo_names(client, org_name)
            repositories = repos_info.get("repositories", [])
        else:
            repositories = repo_names
    except Exception as e:
        _LOG.error("Error retrieving repositories for '%s': %s", org_name, e)
        return {"total_prs": 0, "period": "N/A", "prs_per_repository": {}}
    total_prs = 0
    prs_per_repository = {}
    # Define the date range and ensure they are timezone-aware in UTC.
    since, until = normalize_period_to_utc(period)
    # Iterate over each repository with progress tracking.
    for repo_name in tqdm(
        repositories, desc="Processing repositories", unit="repo"
    ):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_pr_count = 0
            # Fetch pull requests based on the specified state.
            issues = repo.get_issues(state=state, since=since)
            for issue in issues:
                if not issue.pull_request:
                    # Skip if not a pull request
                    continue
                try:
                    pr = repo.get_pull(issue.number)
                except Exception as e:
                    _LOG.warning(
                        "Could not fetch PR #%d in %s: %s",
                        issue.number,
                        repo_name,
                        e,
                    )
                    continue
                # Ensure pr.created_at is timezone-aware in UTC.
                pr_created_at = (
                    pr.created_at.replace(tzinfo=datetime.timezone.utc)
                    if pr.created_at.tzinfo is None
                    else pr.created_at.astimezone(datetime.timezone.utc)
                )
                if since and until and not (since <= pr_created_at <= until):
                    # Skip pull request if it's outside the specified date range.
                    continue
                if usernames and pr.user.login not in usernames:
                    # Skip pull request if it's not authored by one of the specified users.
                    continue
                repo_pr_count += 1
            prs_per_repository[repo_name] = repo_pr_count
            total_prs += repo_pr_count
        except Exception as e:
            _LOG.error(
                "Error accessing pull requests for repository '%s': %s",
                repo_name,
                e,
            )
            prs_per_repository[repo_name] = 0
    result = {
        "total_prs": total_prs,
        "period": f"{since} to {until}" if since and until else "All time",
        "prs_per_repository": prs_per_repository,
    }
    return result


def get_prs_not_merged(
    client: github.Github,
    org_name: str,
    usernames: Optional[List[str]] = None,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    repo_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch the count of closed but unmerged pull requests in the specified
    repositories and by the specified GitHub users within a given period.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :param usernames: GitHub usernames to filter pull requests; if None, fetches for all users
    :param period: start and end datetime for filtering pull requests
    :param repo_names: repository names to fetch PRs from; if None, fetches
        from all repositories in the organization
    :return: a dictionary containing:
        - prs_not_merged (int): total number of closed but unmerged pull requests
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and
            unmerged pull request counts as values
    """
    try:
        if not repo_names:
            # Retrieve repositories for the specified organization.
            repos_info = get_repo_names(client, org_name)
            repositories = repos_info.get("repositories", [])
        else:
            repositories = repo_names
    except Exception as e:
        _LOG.error("Error retrieving repositories for '%s': %s", org_name, e)
        return {
            "prs_not_merged": 0,
            "period": "N/A",
            "prs_per_repository": {},
        }
    total_unmerged_prs = 0
    prs_per_repository = {}
    # Define the date range and ensure they are timezone-aware in UTC.
    since, until = normalize_period_to_utc(period)
    # Iterate over each repository with progress tracking.
    for repo_name in tqdm(
        repositories, desc="Processing repositories", unit="repo"
    ):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_unmerged_pr_count = 0
            # Fetch closed pull requests.
            issues = repo.get_issues(state="closed", since=since)
            pulls = [
                repo.get_pull(issue.number)
                for issue in issues
                if issue.pull_request
            ]
            for pr in pulls:
                try:
                    # Print progress.
                    _LOG.debug("Processing PR #%d from %s", pr.number, repo_name)
                    # Ensure PR creation date is always set before usage.
                    pr_created_at = (
                        pr.created_at if pr.created_at else datetime.datetime.min
                    )
                    if pr_created_at.tzinfo is None:
                        pr_created_at = pr_created_at.replace(
                            tzinfo=datetime.timezone.utc
                        )
                    else:
                        pr_created_at = pr_created_at.astimezone(
                            datetime.timezone.utc
                        )
                    if pr.merged:
                        # Disregard PRs that are merged.
                        continue
                    if usernames and pr.user.login not in usernames:
                        # Skip pull request if it's not authored by one of the specified users.
                        continue
                    if since and until and not (since <= pr_created_at <= until):
                        # Skip pull request if it's outside the specified date range.
                        continue
                    repo_unmerged_pr_count += 1
                except Exception as e:
                    # Skip this PR and proceed with the next one.
                    _LOG.error(
                        "Error processing PR #%d in '%s': %s",
                        pr.number,
                        repo_name,
                        e,
                    )
                    continue
            prs_per_repository[repo_name] = repo_unmerged_pr_count
            total_unmerged_prs += repo_unmerged_pr_count
        except Exception as e:
            _LOG.error(
                "Error accessing pull requests for repository '%s': %s",
                repo_name,
                e,
            )
            prs_per_repository[repo_name] = 0
    result = {
        "prs_not_merged": total_unmerged_prs,
        "period": f"{since} to {until}" if since and until else "All time",
        "prs_per_repository": prs_per_repository,
    }
    return result


def get_total_issues(
    client: github.Github,
    org_name: str,
    repo_names: Optional[List[str]] = None,
    state: str = "open",
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
) -> Dict[str, Any]:
    """
    Retrieve the number of issues in the specified repositories within a given
    time range and state.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :param repo_names: repository names to fetch issues from; if None, fetches
        from all repositories in the organization
    :param state: the state of the issues to consider ('open', 'closed', or
        'all'); default is 'open'
    :param period: start and end datetime for filtering issues; if None,
        considers all time
    :return: a dictionary containing:
        - total_issues (int): total number of issues
        - state (str): the state of the issues considered
        - period (str): the time range considered
        - issues_per_repository (Dict[str, int]): repository names as keys and
          issue counts as values
    """
    total_issues = 0
    issues_per_repository = {}
    since, until = normalize_period_to_utc(period)
    try:
        # Retrieve repositories for the specified organization.
        if not repo_names:
            repos_info = get_repo_names(client, org_name)
            repo_names = repos_info.get("repositories", [])
    except Exception as e:
        _LOG.error("Error retrieving repositories for '%s': %s", org_name, e)
        return {
            "total_issues": 0,
            "state": state,
            "period": "N/A",
            "issues_per_repository": {},
        }
    # Iterate over each repository.
    for repo_name in tqdm(
        repo_names, desc="Processing repositories", unit="repo"
    ):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_issue_count = 0
            issues = repo.get_issues(state=state, since=since)
            for issue in issues:
                try:
                    if issue.pull_request:
                        # Filter and continue if the issue is a pull request.
                        continue
                    # Ensure Issue creation date is timezone-aware in UTC.
                    issue_created_at = (
                        issue.created_at
                        if issue.created_at
                        else datetime.datetime.min
                    )
                    if issue_created_at.tzinfo is None:
                        issue_created_at = issue_created_at.replace(
                            tzinfo=datetime.timezone.utc
                        )
                    else:
                        issue_created_at = issue_created_at.astimezone(
                            datetime.timezone.utc
                        )
                    if (
                        since
                        and until
                        and not (since <= issue_created_at <= until)
                    ):
                        # Skip the issue if it's outside the specified date range.
                        continue
                    repo_issue_count += 1
                except Exception as e:
                    # Skip this issue and proceed with the next one.
                    _LOG.error("Error processing issue in '%s': %s", repo_name, e)
                    continue
            issues_per_repository[repo_name] = repo_issue_count
            total_issues += repo_issue_count
        except Exception as e:
            _LOG.error(
                "Error accessing issues for repository '%s': %s", repo_name, e
            )
            issues_per_repository[repo_name] = 0
    result = {
        "total_issues": total_issues,
        "state": state,
        "period": f"{since} to {until}" if since and until else "All time",
        "issues_per_repository": issues_per_repository,
    }
    return result


def get_issues_without_assignee(
    client: github.Github,
    org_name: str,
    repo_names: Optional[List[str]] = None,
    state: str = "open",
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
) -> Dict[str, Any]:
    """
    Retrieve the number of issues without an assignee within a specified time
    range and state.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :param repo_names: repository names to fetch issues from; if None, fetches
        from all repositories in the organization
    :param state: the state of the issues to consider ('open', 'closed', or 'all')
    :param period: start and end datetime for filtering issues; if None,
        considers all time
    :return: a dictionary containing:
        - issues_without_assignee (int): total number of issues without an assignee
        - state (str): the state of the issues considered
        - period (str): the time range considered
        - issues_per_repository (Dict[str, int]): repository names as keys and
          unassigned issue counts as values
    """
    issues_without_assignee = 0
    issues_per_repository = {}
    since, until = normalize_period_to_utc(period)
    try:
        # Retrieve repositories for the specified organization
        if not repo_names:
            repos_info = get_repo_names(client, org_name)
            repo_names = repos_info.get("repositories", [])
    except Exception as e:
        _LOG.error("Error retrieving repositories for '%s': %s", org_name, e)
        return {
            "issues_without_assignee": 0,
            "state": state,
            "period": "N/A",
            "issues_per_repository": {},
        }
    for repo_name in tqdm(
        repo_names, desc="Processing repositories", unit="repo"
    ):
        try:
            repo = client.get_repo(f"{org_name}/{repo_name}")
            repo_unassigned_count = 0
            issues = repo.get_issues(state=state, since=since)
            for issue in issues:
                try:
                    if issue.pull_request:
                        # Filter and continue if the issue is a pull request.
                        continue
                    # Ensure Issue creation date is timezone-aware in UTC.
                    issue_created_at = (
                        issue.created_at
                        if issue.created_at
                        else datetime.datetime.min
                    )
                    if issue_created_at.tzinfo is None:
                        issue_created_at = issue_created_at.replace(
                            tzinfo=datetime.timezone.utc
                        )
                    else:
                        issue_created_at = issue_created_at.astimezone(
                            datetime.timezone.utc
                        )
                    if (
                        since
                        and until
                        and not (since <= issue_created_at <= until)
                    ):
                        # Skip the issue if it's outside the specified date range.
                        continue
                    if not issue.assignees:
                        repo_unassigned_count += 1
                except Exception as e:
                    _LOG.error("Error processing issue in '%s': %s", repo_name, e)
                    continue
            issues_per_repository[repo_name] = repo_unassigned_count
            issues_without_assignee += repo_unassigned_count
        except Exception as e:
            _LOG.error(
                "Error accessing issues for repository '%s': %s", repo_name, e
            )
            issues_per_repository[repo_name] = 0
    result = {
        "issues_without_assignee": issues_without_assignee,
        "state": state,
        "period": f"{since} to {until}" if since and until else "All time",
        "issues_per_repository": issues_per_repository,
    }
    return result


# #############################################################################
# Individual User Metrics APIs
# #############################################################################


def get_commits_by_person(
    client: github.Github,
    username: str,
    org_name: str,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    repo_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Retrieve the number of commits made by a specific GitHub user.

    :param client: authenticated instance of the PyGithub client
    :param username: GitHub username to fetch commit data for
    :param org_name: name of the GitHub organization
    :param period: start and end datetime for filtering commits
    :param repo_names: repository names to fetch commits from; if None, fetches
        from all repositories in the organization
    :return: a dictionary containing:
        - user (str): GitHub username
        - total_commits (int): total number of commits made by the user
        - period (str): the time range considered
        - commits_per_repository (Dict[str, int]): repository names as keys and
          commit counts as values
    """
    result = get_total_commits(
        client=client,
        org_name=org_name,
        usernames=[username],
        period=period,
        repo_names=repo_names,
    )
    return {
        "user": username,
        "total_commits": result["total_commits"],
        "period": result["period"],
        "commits_per_repository": result["commits_per_repository"],
    }


def get_prs_by_person(
    client: github.Github,
    username: str,
    org_name: str,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    state: str = "open",
    repo_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch the number of pull requests created by a specific GitHub user in the
    given repositories and time period.

    :param client: authenticated instance of the PyGithub client
    :param username: GitHub username to fetch pull request data for
    :param org_name: name of the GitHub organization
    :param period: start and end datetime for filtering pull requests
    :param state: state of the pull requests to fetch; can be 'open', 'closed',
        or 'all'
    :param repo_names: repository names to fetch commits from; if None, fetches
        from all repositories in the organization
    :return: a dictionary containing:
        - user (str): GitHub username
        - total_prs (int): total number of pull requests created
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and pull
          request counts as values
    """
    result = get_total_prs(
        client=client,
        org_name=org_name,
        usernames=[username],
        period=period,
        state=state,
        repo_names=repo_names,
    )
    return {
        "user": username,
        "total_prs": result["total_prs"],
        "period": result["period"],
        "prs_per_repository": result["prs_per_repository"],
    }


def get_prs_not_merged_by_person(
    client: github.Github,
    username: str,
    org_name: str,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    repo_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch the number of closed but unmerged pull requests created by a specific
    GitHub user in the given repositories and time period.

    :param client: authenticated instance of the PyGithub client
    :param username: GitHub username to fetch unmerged pull request data for
    :param org_name: name of the GitHub organization
    :param period: start and end datetime for filtering pull requests
    :param repo_names: repository names to fetch commits from; if None, fetches
        from all repositories in the organization
    :return: a dictionary containing:
        - user (str): GitHub username
        - prs_not_merged (int): total number of closed but unmerged pull requests
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and
          unmerged PR counts as values
    """
    result = get_prs_not_merged(
        client=client,
        org_name=org_name,
        usernames=[username],
        period=period,
        repo_names=repo_names,
    )
    return {
        "user": username,
        "prs_not_merged": result["prs_not_merged"],
        "period": result["period"],
        "prs_per_repository": result["prs_per_repository"],
    }


# #############################################################################
# Stats Comparison APIs
# #############################################################################


def collect_user_statistics(
    client: github.Github,
    usernames: List[str],
    org_name: str,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    repo_names: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Collect GitHub activity metrics for a list of users with rate-limit-aware
    retry logic. Includes total commits, PRs, additions, deletions, and
    repository-level breakdown.

    :param client: authenticated instance of the PyGithub client
    :param usernames: list of GitHub usernames to process
    :param org_name: name of the GitHub organization
    :param period: optional tuple of start and end datetime for filtering activity
    :param repo_names: optional list of repositories to scope the query; if None, uses all repos in org
    :return: list of dictionaries containing per-user statistics, including:
        - Username (str)
        - Total Commits (int)
        - Total PRs (int)
        - Total Additions (int)
        - Total Deletions (int)
        - Total Changes (int)
        - Repo Breakdown (Dict[str, Dict[str, int]])
    """
    results = []
    pending_usernames = usernames.copy()
    while pending_usernames:
        username = pending_usernames[0]
        try:
            print(f"Processing user: {username}")
            wait_for_rate_limit_reset(client)
            commits_data = get_commits_by_person(
                client=client,
                username=username,
                org_name=org_name,
                period=period,
                repo_names=repo_names,
            )
            wait_for_rate_limit_reset(client)
            prs_data = get_prs_by_person(
                client=client,
                username=username,
                org_name=org_name,
                period=period,
                state="all",
                repo_names=repo_names,
            )
            total_commits = commits_data["total_commits"]
            total_additions = 0
            total_deletions = 0
            repo_breakdown = {}
            for repo, branches in commits_data["commits_per_repository"].items():
                repo_add = 0
                repo_del = 0
                repo_commit = 0
                repo_master_commit = 0
                for branch, stats in branches.items():
                    repo_add += stats["additions"]
                    repo_del += stats["deletions"]
                    repo_commit += stats["commits"]
                    if branch == "master":
                        repo_master_commit = stats["commits"]
                repo_breakdown[repo] = {
                    "repo_commits": repo_commit,
                    "repo_master_commits": repo_master_commit,
                    "repo_additions": repo_add,
                    "repo_deletions": repo_del,
                    "repo_total_changes": repo_add + repo_del,
                }
                total_additions += repo_add
                total_deletions += repo_del
            results.append(
                {
                    "Username": username,
                    "Total Commits": total_commits,
                    "Total PRs": prs_data["total_prs"],
                    "Total Additions": total_additions,
                    "Total Deletions": total_deletions,
                    "Total Changes": total_additions + total_deletions,
                    "Repo Breakdown": repo_breakdown,
                }
            )
            pending_usernames.pop(0)
            print(f"Finished processing user: {username}")
        except Exception as e:
            _LOG.error(
                "Error occurred while processing user '%s': %s", username, e
            )
            print(f"Retrying user after rate-limit reset: {username}")
            pending_usernames.insert(0, username)
            wait_for_rate_limit_reset(client)
    return results


def extract_commits_to_master(df_comparison: "pd.DataFrame") -> "pd.DataFrame":
    """
    Extract the 'Repo Breakdown' column of the user comparison dataframe to
    extract the number of commits to the 'master' branch for each user and
    repository.

    :param df_comparison: DataFrame containing user-level GitHub activity metrics.
                          It must contain columns:
                            - 'Username' (str)
                            - 'Repo Breakdown' (Dict[str, Dict[str, int]])
    :return: A DataFrame with one row per (user, repository) pair, containing:
             - Username (str)
             - Repository (str)
             - Commits to Master (int) – only for repos with > 0 master commits
    """
    repo_master_commit_records = []
    for _, row in df_comparison.iterrows():
        username = row["Username"]
        repo_breakdown = row.get("Repo Breakdown", {})
        for repo_name, repo_stats in repo_breakdown.items():
            master_commits = repo_stats.get("repo_master_commits", 0)
            if master_commits > 0:
                repo_master_commit_records.append(
                    {
                        "Username": username,
                        "Repository": repo_name,
                        "Commits to Master": master_commits,
                    }
                )
    return pd.DataFrame(repo_master_commit_records)
