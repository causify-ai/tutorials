<!-- toc -->

- [GitHub API Wrapper Documentation](#github-api-wrapper-documentation)
  * [GitHub Endpoints Used in the Wrapper](#github-endpoints-used-in-the-wrapper)
    + [1. Commits API](#1-commits-api)
    + [2. Pull Requests API](#2-pull-requests-api)
    + [3. Issues API](#3-issues-api)
    + [4. Repositories API](#4-repositories-api)
    + [5. Contributors API](#5-contributors-api)
  * [Core Wrapper Functions](#core-wrapper-functions)
    + [1. `GitHubAPI`](#1-githubapi)
    + [2. `get_repo_names`](#2-get_repo_names)
    + [3. `get_github_contributors`](#3-get_github_contributors)
    + [4. `normalize_period_to_utc`](#4-normalize_period_to_utc)
  * [Global Metrics Functions](#global-metrics-functions)
    + [1. `get_total_commits`](#1-get_total_commits)
    + [2. `get_total_prs`](#2-get_total_prs)
    + [3. `get_prs_not_merged`](#3-get_prs_not_merged)
    + [4. `get_total_issues`](#4-get_total_issues)
    + [5. `get_issues_without_assignee`](#5-get_issues_without_assignee)
  * [User-Centric Wrapper Functions](#user-centric-wrapper-functions)
    + [1. `get_commits_by_person`](#1-get_commits_by_person)
    + [2. `get_prs_by_person`](#2-get_prs_by_person)
    + [3. `get_prs_not_merged_by_person`](#3-get_prs_not_merged_by_person)
    + [4. `get_issues_by_person`](#4-get_issues_by_person)
  * [Real-Life Use Cases](#real-life-use-cases)
  * [Authentication](#authentication)

<!-- tocstop -->

# GitHub API Wrapper Documentation

This document outlines the core endpoints and utility functions provided in the
`github_utils.py` module. The purpose of this wrapper is to simplify GitHub
analytics for developer performance tracking and team productivity insights.

## GitHub Endpoints Used in the Wrapper

### 1. Commits API

- Endpoint: `GET /repos/{owner}/{repo}/commits`
  - Usage: Retrieves commits for a repository, optionally filtered by author and
    date range.

### 2. Pull Requests API

- Endpoint: `GET /repos/{owner}/{repo}/pulls`
  - Usage: Fetches pull requests based on state (open, closed, all).
- Endpoint: `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - Usage: Fetches metadata about an individual PR, such as author and merge
    status.

### 3. Issues API

- Endpoint: `GET /repos/{owner}/{repo}/issues`
  - Usage: Retrieves issues, optionally filtered by state and since date. Used
    for counting issues and filtering unassigned ones.

### 4. Repositories API

- Endpoint: `GET /orgs/{org}/repos`
  - Usage: Fetches all repositories under a specific organization.

### 5. Contributors API

- Endpoint: `GET /repos/{owner}/{repo}/contributors`
  - Usage: Returns contributors to a repository along with commit counts.

## Core Wrapper Functions

### 1. `GitHubAPI`

Initializes an authenticated GitHub client using a personal access token (PAT).

- Automatically detects token from environment or accepts explicitly.
- Handles both public GitHub and GitHub Enterprise (custom base URL).

### 2. `get_repo_names`

- Returns all repositories under a GitHub organization.

  **Returns**:

  ```python
  {
      "owner": "org_name",
      "repositories": ["repo1", "repo2", ...]
  }
  ```

### 3. `get_github_contributors`

- Retrieves all contributors across a list of repositories.

  **Returns**:

  ```python
  {
      "org/repo1": ["user1", "user2", ...],
      ...
  }
  ```

### 4. `normalize_period_to_utc`

- Converts naive or local datetime objects into UTC-aware datetimes.

## Global Metrics Functions

### 1. `get_total_commits`

- Computes the total number of commits across all repositories in an
  organization.
- Optionally filtered by usernames and a time period.

### 2. `get_total_prs`

- Computes the number of PRs by state (`open`, `closed`, or `all`) within an
  org.
- Optionally filtered by usernames and time period.

### 3. `get_prs_not_merged`

- Identifies closed PRs that were never merged.

  **Use case**: Detect abandoned or rejected PRs.

### 4. `get_total_issues`

- Retrieves issue counts across all repositories, excluding PRs.
- Allows filtering by state and time window.

### 5. `get_issues_without_assignee`

- Returns the number of issues that have no assignee, useful for task triage.

## User-Centric Wrapper Functions

These functions wrap global metrics to return results for individual users.

### 1. `get_commits_by_person`

- Returns total commits made by a specific GitHub user, along with repository
  breakdown.

### 2. `get_prs_by_person`

- Returns number of PRs opened by a specific user, optionally filtered by state.

### 3. `get_prs_not_merged_by_person`

- Returns unmerged PRs authored by a specific user.

### 4. `get_issues_by_person`

- Returns number of issues authored by a specific user.

## Real-Life Use Cases

These functions are designed to support practical workflows:

- **Performance Reviews**: Use user-specific metrics to track engineering KPIs.
- **Top Contributor Reports**: Rank users based on commit/PR stats.
- **Sprint Planning**: Visualize developer throughput across projects.
- **Pull Request Hygiene**: Monitor unmerged or stale PRs to improve code review
  cycles.
- **Productivity Dashboards**: Build Streamlit or Dash apps using structured
  JSON outputs.

## Authentication

All functions require a GitHub PAT (Personal Access Token) with appropriate
scopes:

```bash
export GITHUB_ACCESS_TOKEN="your_token"
```

Scopes required:

- `repo` (for private repo access)
- `read:org` (to fetch org members and repositories)
