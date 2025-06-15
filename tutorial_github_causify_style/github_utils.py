"""
Import as:

import tutorial_github_causify_style.github_utils as tgcsgiut
"""

import datetime
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import github
import helpers.hcache_simple as hcacsimp
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

_LOG = logging.getLogger(__name__)


# #############################################################################
# GitHubAPI
# #############################################################################


class GitHubAPI:
    """
    Initialize and manage authentication with the GitHub API using PyGithub.
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


# TODO(prahar08modi): Test the function using pytest
def get_repo_names(client: github.Github, org_name: str) -> Dict[str, List[str]]:
    """
    Retrieve a list of repositories under a specific organization.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :return: a dictionary containing:
        - owner: name of the organization
        - repositories: repository names
    """
    # TODO: Turn the try-except into an assertion. No point in trying to recover.
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


# TODO(prahar08modi): Test the function using pytest
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
    :return: UTC-aware start and end datetime, or (None, None) if period
        is None
    """
    # TODO: Code implementation-137: Use `if period is None` instead of `if not period` to check if `period` is `None`.
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


# #############################################################################
# Global Metrics APIs
# #############################################################################


def get_total_commits(
    client: github.Github,
    org_name: str,
    usernames: Optional[List[str]] = None,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
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
    :return: a dictionary containing:
        - total_commits (int): total number of commits across all repositories
        - period (str): the time range considered
        - commits_per_repository (Dict[str, int]): repository names as keys and
          commit counts as values
    """
    try:
        # Retrieve repositories for the specified organization.
        repos_info = get_repo_names(client, org_name)
        repositories = repos_info.get("repositories", [])
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
            repo_commit_count = 0
            if usernames:
                for username in usernames:
                    commits = repo.get_commits(
                        author=username, since=since, until=until
                    )
                    repo_commit_count += commits.totalCount
            else:
                commits = repo.get_commits(since=since, until=until)
                repo_commit_count = commits.totalCount
            commits_per_repository[repo_name] = repo_commit_count
            total_commits += repo_commit_count
        except Exception as e:
            _LOG.error(
                "Error accessing commits for repository '%s': %s", repo_name, e
            )
            commits_per_repository[repo_name] = 0
    result = {
        "total_commits": total_commits,
        "period": f"{since} to {until}" if since and until else "All time",
        "commits_per_repository": commits_per_repository,
    }
    return result


def get_total_prs(
    client: github.Github,
    org_name: str,
    usernames: Optional[List[str]] = None,
    period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
    state: str = "all",
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
    :return: a dictionary containing:
        - total_prs (int): total number of pull requests
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and pull
            request counts as values
    """
    try:
        # Retrieve repositories for the specified organization.
        repos_info = get_repo_names(client, org_name)
        repositories = repos_info.get("repositories", [])
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
            pulls = repo.get_pulls(state=state)
            for pr in pulls:
                if usernames and pr.user.login not in usernames:
                    continue
                pr_created_at = (
                    pr.created_at.replace(tzinfo=datetime.timezone.utc)
                    if pr.created_at.tzinfo is None
                    else pr.created_at.astimezone(datetime.timezone.utc)
                )
                if since and until and not (since <= pr_created_at <= until):
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
) -> Dict[str, Any]:
    """
    Fetch the count of closed but unmerged pull requests in the specified
    repositories and by the specified GitHub users within a given period.

    :param client: authenticated instance of the PyGithub client
    :param org_name: name of the GitHub organization
    :param usernames: GitHub usernames to filter pull requests; if None, fetches for all users
    :param period: start and end datetime for filtering pull requests
    :return: a dictionary containing:
        - prs_not_merged (int): total number of closed but unmerged pull requests
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and
            unmerged pull request counts as values
    """
    try:
        # Retrieve repositories for the specified organization.
        repos_info = get_repo_names(client, org_name)
        repositories = repos_info.get("repositories", [])
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
    state: str = "all",
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
) -> Dict[str, Any]:
    """
    Retrieve the number of commits made by a specific GitHub user.

    :param client: authenticated instance of the PyGithub client
    :param username: GitHub username to fetch commit data for
    :param org_name: name of the GitHub organization
    :param period: start and end datetime for filtering commits
    :return: a dictionary containing:
        - user (str): GitHub username
        - total_commits (int): total number of commits made by the user
        - period (str): the time range considered
        - commits_per_repository (Dict[str, int]): repository names as keys and
          commit counts as values
    """
    result = get_total_commits(
        client=client, org_name=org_name, usernames=[username], period=period
    )
    # TODO(False): Functions-224: Do not put computations of the output in the `return` line. Compute the output first, assign it to a variable, and then return this variable.
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
    state: str = "all",
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
    )
    # TODO(False): Functions-224: Do not put computations of the output in the `return` line. Compute the output first, assign it to a variable, and then return this variable.
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
) -> Dict[str, Any]:
    """
    Fetch the number of closed but unmerged pull requests created by a specific
    GitHub user in the given repositories and time period.

    :param client: authenticated instance of the PyGithub client
    :param username: GitHub username to fetch unmerged pull request data for
    :param org_name: name of the GitHub organization
    :param period: start and end datetime for filtering pull requests
    :return: a dictionary containing:
        - user (str): GitHub username
        - prs_not_merged (int): total number of closed but unmerged pull requests
        - period (str): the time range considered
        - prs_per_repository (Dict[str, int]): repository names as keys and
          unmerged PR counts as values
    """
    result = get_prs_not_merged(
        client=client, org_name=org_name, usernames=[username], period=period
    )
    # TODO(False): Functions-224: Do not put computations of the output in the `return` line. Compute the output first, assign it to a variable, and then return this variable.
    return {
        "user": username,
        "prs_not_merged": result["prs_not_merged"],
        "period": result["period"],
        "prs_per_repository": result["prs_per_repository"],
    }


def days_between(
    period: Tuple[datetime.datetime, datetime.datetime],
) -> List[datetime.date]:
    """
    Generate each date in time span.

    :param period: start and end datetime
    :return: date span
    """
    start_date = period[0].date()
    end_date = period[1].date()
    days: List[datetime.date] = []
    current = start_date
    while current <= end_date:
        days.append(current)
        current += datetime.timedelta(days=1)
    # TODO(False): Logging-248: Use `_LOG.debug()` instead of `_LOG.info()` for tracing execution.
    _LOG.info("Generated %d days in period.", len(days))
    return days


@hcacsimp.simple_cache(cache_type="json", write_through=True)
def get_commit_datetimes_by_repo_period_intrinsic(
    client,
    org: str,
    repo: str,
    username: Optional[str],
    since: datetime.datetime,
    until: datetime.datetime,
) -> List[str]:
    """
    Fetch commit timestamps for user in repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param since: start datetime
    :param until: end datetime
    :return: commit timestamps in ISO format
    """
    timestamps: List[str] = []
    try:
        repo_obj = client.get_repo(f"{org}/{repo}")
        # Grab all commits in range, then filter by author or committer.
        for c in repo_obj.get_commits(since=since, until=until):
            author_login = c.author.login if c.author else None
            committer_login = c.committer.login if c.committer else None
            if username in (author_login, committer_login):
                dt = c.commit.author.date
                dt_utc = (
                    dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
                )
                timestamps.append(dt_utc.isoformat())
        _LOG.info(
            "Fetched %d commits for %s/%s user=%s.",
            len(timestamps),
            org,
            repo,
            username,
        )
    except Exception as e:
        _LOG.warning(
            "Failed to fetch commits for %s/%s user=%s: %s.",
            org,
            repo,
            username,
            e,
        )
    return timestamps


@hcacsimp.simple_cache(cache_type="json", write_through=True)
def get_pr_datetimes_by_repo_period_intrinsic(
    client,
    org: str,
    repo: str,
    username: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> List[str]:
    """
    Fetch pull request timestamps for user in repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param since: start datetime
    :param until: end datetime
    :return: PR created timestamps in ISO format
    """
    timestamps: List[str] = []
    since_date = since.date().isoformat()
    until_date = until.date().isoformat()
    query = f"repo:{org}/{repo} is:pr author:{username} created:{since_date}..{until_date}"
    try:
        results = client.search_issues(query)
        for issue in results:
            dt = issue.created_at
            dt_utc = dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
            timestamps.append(dt_utc.isoformat())
        _LOG.info(
            "Found %d PRs for %s/%s user=%s.",
            len(timestamps),
            org,
            repo,
            username,
        )
    except Exception as e:
        _LOG.warning(
            "PR search failed for %s/%s user=%s: %s.", org, repo, username, e
        )
    return timestamps


@hcacsimp.simple_cache(cache_type="json", write_through=True)
def get_loc_stats_by_repo_period_intrinsic(
    client,
    org: str,
    repo: str,
    username: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> List[Dict[str, int]]:
    """
    Fetch commit LOC stats for user in repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param since: start datetime
    :param until: end datetime
    :return: additions, deletions in code
    """
    stats_list: List[Dict[str, int]] = []
    try:
        repo_obj = client.get_repo(f"{org}/{repo}")
        # Grab all commits in range, then filter by author/committer.
        for c in repo_obj.get_commits(since=since, until=until):
            author_login = c.author.login if c.author else None
            committer_login = c.committer.login if c.committer else None
            if username not in (author_login, committer_login):
                continue
            try:
                s = c.stats
            except Exception:
                _LOG.warning("Could not fetch stats for commit %s.", c.sha)
                continue
            dt = c.commit.author.date
            dt_utc = dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
            iso = dt_utc.date().isoformat()
            stats_list.append(
                {"date": iso, "additions": s.additions, "deletions": s.deletions}
            )
        _LOG.info(
            "Fetched LOC stats for %s/%s user=%s entries=%d.",
            org,
            repo,
            username,
            len(stats_list),
        )
    except Exception as e:
        _LOG.warning(
            "Failed to fetch LOC for %s/%s user=%s: %s.", org, repo, username, e
        )
    return stats_list


def build_daily_commit_df(
    client,
    org: str,
    repo: str,
    username: str,
    period: Tuple[datetime.datetime, datetime.datetime],
) -> pd.DataFrame:
    """
    Build daily commit counts for user and repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param period: start and end datetime objects
    :return: data with date, commits, repo, user
    """
    since, until = period
    timestamps = get_commit_datetimes_by_repo_period_intrinsic(
        client, org, repo, username, since, until
    )
    df = pd.DataFrame({"ts": pd.to_datetime(timestamps)})
    df["date"] = df.ts.dt.date
    daily = df.groupby("date").size().reset_index(name="commits")
    all_days = pd.DataFrame({"date": days_between(period)})
    daily = all_days.merge(daily, on="date", how="left")
    daily["commits"] = daily["commits"].fillna(0).astype(int)
    daily["repo"] = repo
    daily["user"] = username
    _LOG.info("Built daily commit DataFrame rows=%d.", len(daily))
    return daily


def build_daily_pr_df(
    client,
    org: str,
    repo: str,
    username: str,
    period: Tuple[datetime.datetime, datetime.datetime],
) -> pd.DataFrame:
    """
    Build daily PR counts for user and repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param period: start and end datetime objects
    :return: data with date, prs, repo, user
    """
    since, until = period
    timestamps = get_pr_datetimes_by_repo_period_intrinsic(
        client, org, repo, username, since, until
    )
    df = pd.DataFrame({"ts": pd.to_datetime(timestamps)})
    df["date"] = df.ts.dt.date
    daily = df.groupby("date").size().reset_index(name="prs")
    all_days = pd.DataFrame({"date": days_between(period)})
    daily = all_days.merge(daily, on="date", how="left")
    daily["prs"] = daily["prs"].fillna(0).astype(int)
    daily["repo"] = repo
    daily["user"] = username
    _LOG.info("Built daily PR DataFrame rows=%d.", len(daily))
    return daily


def build_daily_loc_df(
    client,
    org: str,
    repo: str,
    username: str,
    period: Tuple[datetime.datetime, datetime.datetime],
) -> pd.DataFrame:
    """
    Build daily LOC additions and deletions for user and repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param period: start and end datetime objects
    :return: data with date, additions, deletions, repo, user
    """
    since, until = period
    # Fetch raw LOC stats list.
    stats_list = get_loc_stats_by_repo_period_intrinsic(
        client, org, repo, username, since, until
    )
    # If no stats, return zeros for full range.
    if not stats_list:
        all_days = pd.DataFrame({"date": days_between(period)})
        # Initialize zeroes.
        all_days["additions"] = all_days["date"].apply(lambda _: 0)
        all_days["deletions"] = all_days["date"].apply(lambda _: 0)
        # Format signs.
        all_days["additions"] = (
            all_days["additions"].astype(str).apply(lambda x: "+" + x)
        )
        all_days["deletions"] = (
            all_days["deletions"].astype(str).apply(lambda x: "-" + x)
        )
        # Add context.
        all_days["repo"] = repo
        all_days["user"] = username
        # TODO(False): Logging-248: Use `_LOG.debug()` instead of `_LOG.info()` for tracing execution.
        _LOG.info("Built daily LOC DataFrame rows=%d (no data).", len(all_days))
        return all_days
    # Otherwise build from stats_list.
    df = pd.DataFrame(stats_list)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    # Sum per date.
    daily = df.groupby("date")[["additions", "deletions"]].sum().reset_index()
    # Ensure full date coverage.
    all_days = pd.DataFrame({"date": days_between(period)})
    daily = all_days.merge(daily, on="date", how="left")
    # Fill missing and integerize.
    daily[["additions", "deletions"]] = (
        daily[["additions", "deletions"]].fillna(0).astype(int)
    )
    # Apply sign formatting.
    daily["additions"] = daily["additions"].astype(str).apply(lambda x: "+" + x)
    daily["deletions"] = daily["deletions"].astype(str).apply(lambda x: "-" + x)
    # Add context.
    daily["repo"] = repo
    daily["user"] = username
    # TODO(False): Logging-248: Use `_LOG.debug()` instead of `_LOG.info()` for tracing execution.
    _LOG.info("Built daily LOC DataFrame rows=%d.", len(daily))
    return daily


def get_total_loc_for_period(
    client,
    org: str,
    repo: str,
    username: str,
    period: Tuple[datetime.datetime, datetime.datetime],
) -> Dict[str, int]:
    """
    Get total LOC additions and deletions for user and repo over period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repo: repository name
    :param username: GitHub username
    :param period: start and end datetime objects
    :return: additions and deletions totals
    """
    since, until = period
    stats = get_loc_stats_by_repo_period_intrinsic(
        client, org, repo, username, since, until
    )
    total_add = sum(item["additions"] for item in stats)
    total_del = sum(item["deletions"] for item in stats)
    _LOG.info(
        "Total LOC for %s/%s user=%s => +%d -%d.",
        org,
        repo,
        username,
        total_add,
        total_del,
    )
    return {"additions": total_add, "deletions": total_del}


def prefetch_periodic_user_repo_data(
    client,
    org: str,
    repos: List[str],
    users: List[str],
    period: Tuple[datetime.datetime, datetime.datetime],
) -> None:
    """
    Prefetch and cache commits, PRs, and LOC for each user and repo over
    period.

    :param client: authenticated PyGithub client
    :param org: GitHub org name
    :param repos: list of repository names
    :param users: list of GitHub usernames
    :param period: start and end datetime objects
    """
    # Validate org, repos, and users types.
    if not isinstance(org, str):
        raise ValueError(f"org must be a string, got {type(org).__name__}")
    if not isinstance(repos, list) or not all(isinstance(r, str) for r in repos):
        raise ValueError("repos must be a list of strings")
    if not isinstance(users, list) or not all(isinstance(u, str) for u in users):
        raise ValueError("users must be a list of strings")
    start = time.time()
    count = 0
    since, until = period
    # Loop over each repo and user combination.
    for repo in repos:
        # Ensure each repo is string.
        if not isinstance(repo, str):
            raise ValueError(f"Expected repo to be a string but got {repo!r}")
        _LOG.info("Starting prefetch for repo %s.", repo)
        for user in users:
            # Ensure each user is string.
            if not isinstance(user, str):
                raise ValueError(f"Expected user to be a string but got {user!r}")
            get_commit_datetimes_by_repo_period_intrinsic(
                client, org, repo, user, since, until
            )
            get_pr_datetimes_by_repo_period_intrinsic(
                client, org, repo, user, since, until
            )
            get_loc_stats_by_repo_period_intrinsic(
                client, org, repo, user, since, until
            )
            count += 1
    elapsed = time.time() - start
    _LOG.info(
        "Prefetched %d user-repo combos in %.2f seconds for period %s to %s.",
        count,
        elapsed,
        period[0],
        period[1],
    )


def collect_all_metrics(
    client,
    org: str,
    repos: List[str],
    users: List[str],
    period: Tuple[datetime.datetime, datetime.datetime],
) -> pd.DataFrame:
    """
    Collect daily metrics for all user-repo combinations.

    :param client: authenticated PyGithub client
    :param org: github org name
    :param repos: repository names
    :param users: github usernames
    :param period: start and end datetime
    :return: concatenated data with date, commits, prs, additions,
        deletions, repo, user
    """
    combined_frames: List[pd.DataFrame] = []
    for repo in repos:
        # Ensure repo is a string.
        if not isinstance(repo, str):
            raise ValueError(f"Expected repo to be a string but got {repo!r}")
        for user in users:
            # Ensure user is a string.
            if not isinstance(user, str):
                raise ValueError(f"Expected user to be a string but got {user!r}")
            # Build each metric DataFrame.
            df_c = build_daily_commit_df(client, org, repo, user, period)
            df_p = build_daily_pr_df(client, org, repo, user, period)
            df_l = build_daily_loc_df(client, org, repo, user, period)
            # Merge on date, repo, and user.
            df = df_c.merge(df_p, on=["date", "repo", "user"], how="inner").merge(
                df_l, on=["date", "repo", "user"], how="inner"
            )
            combined_frames.append(df)
    # Concatenate all DataFrames or return empty.
    combined = (
        pd.concat(combined_frames, ignore_index=True)
        if combined_frames
        else pd.DataFrame()
    )
    return combined


# Separate summary functions for user-repo and repo-user metrics for clarity.
def summarize_user_metrics_for_repo(
    combined: pd.DataFrame, repo: str
) -> pd.DataFrame:
    """
    Summarize total commits, PRs, and LOC per user in a specific repository.

    :param combined: data with all metrics
    :param repo: repository name
    :return: data with columns user, commits, prs, additions, deletions
    """
    df = combined[combined["repo"] == repo].copy()
    df["additions"] = df["additions"].str.replace("+", "").astype(int)
    df["deletions"] = df["deletions"].str.replace("-", "").astype(int)
    summary = (
        df.groupby("user")
        .agg(
            commits=pd.NamedAgg(column="commits", aggfunc="sum"),
            prs=pd.NamedAgg(column="prs", aggfunc="sum"),
            additions=pd.NamedAgg(column="additions", aggfunc="sum"),
            deletions=pd.NamedAgg(column="deletions", aggfunc="sum"),
        )
        .reset_index()
    )
    return summary


def summarize_repo_metrics_for_user(
    combined: pd.DataFrame, user: str
) -> pd.DataFrame:
    """
    Summarize total commits, PRs, and LOC per repository for a specific user.

    :param combined: data with all metrics
    :param user: GitHub username
    :return: data with columns repo, commits, prs, additions, deletions
    """
    df = combined[combined["user"] == user].copy()
    df["additions"] = df["additions"].str.replace("+", "").astype(int)
    df["deletions"] = df["deletions"].str.replace("-", "").astype(int)
    summary = (
        df.groupby("repo")
        .agg(
            commits=pd.NamedAgg(column="commits", aggfunc="sum"),
            prs=pd.NamedAgg(column="prs", aggfunc="sum"),
            additions=pd.NamedAgg(column="additions", aggfunc="sum"),
            deletions=pd.NamedAgg(column="deletions", aggfunc="sum"),
        )
        .reset_index()
    )
    return summary


def plot_metrics_by_user(
    summary: pd.DataFrame, repo: str, metrics: Optional[List[str]] = None
) -> None:
    """
    Plot specified metrics for users in a single repo as grouped bar chart.

    :param summary: data with summary from `compare_user_repo_summary`
    :param repo: repository name
    :param metrics: metrics to plot (commits, prs, additions, deletions)
    """
    # Determine which metrics to plot.
    available = ["commits", "prs", "additions", "deletions"]
    to_plot = metrics if metrics else available
    # Validate metrics.
    for m in to_plot:
        if m not in available:
            raise ValueError(f"Unsupported metric '{m}'")
    x = list(range(len(to_plot)))
    n_users = len(summary)
    width = 0.8 / n_users if n_users else 0.8
    fig, ax = plt.subplots()
    # Plot bars and annotate counts.
    for idx, user in enumerate(summary["user"]):
        values = (
            summary.loc[summary["user"] == user, to_plot]
            .astype(int)
            .iloc[0]
            .tolist()
        )
        positions = [i + idx * width for i in x]
        bars = ax.bar(positions, values, width=width, label=user)
        for b in bars:
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height(),
                str(int(b.get_height())),
                ha="center",
                va="bottom",
            )
    # Center tick labels under bar groups.
    ax.set_xticks([i + width * (n_users - 1) / 2 for i in x])
    ax.set_xticklabels([m.capitalize() for m in to_plot])
    ax.set_ylabel("Count")
    # Update title format per user request.
    ax.set_title(f"Metric comparison for {repo} Repo")
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_metrics_by_repo(
    summary: pd.DataFrame, user: str, metrics: Optional[List[str]] = None
) -> None:
    """
    Plot specified metrics for repos for a single user as grouped bar chart.

    :param summary: data with summary from `compare_user_across_repos_summary`
    :param user: github username
    :param metrics: metrics to plot (commits, prs, additions, deletions)
    """
    # Determine which metrics to plot.
    available = ["commits", "prs", "additions", "deletions"]
    to_plot = metrics if metrics else available
    # Validate metrics.
    for m in to_plot:
        if m not in available:
            raise ValueError(f"Unsupported metric '{m}'")
    x = list(range(len(to_plot)))
    n_repos = len(summary)
    width = 0.8 / n_repos if n_repos else 0.8
    fig, ax = plt.subplots()
    # Plot bars and annotate counts.
    for idx, repo in enumerate(summary["repo"]):
        values = (
            summary.loc[summary["repo"] == repo, to_plot]
            .astype(int)
            .iloc[0]
            .tolist()
        )
        positions = [i + idx * width for i in x]
        bars = ax.bar(positions, values, width=width, label=repo)
        for b in bars:
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height(),
                str(int(b.get_height())),
                ha="center",
                va="bottom",
            )
    # Center tick labels under bar groups.
    ax.set_xticks([i + width * (n_repos - 1) / 2 for i in x])
    ax.set_xticklabels([m.capitalize() for m in to_plot])
    ax.set_ylabel("Count")
    # Update title format per user request.
    ax.set_title(f"Metric comparison for {user} across repos")
    ax.legend()
    plt.tight_layout()
    plt.show()
