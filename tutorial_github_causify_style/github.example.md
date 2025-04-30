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

# Authentication

## Getting token

To authenticate and interact with the GitHub API, you’ll need a **Personal Access
Token** with appropriate scopes (permissions). Follow the steps below to generate
one:

1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens) while logged into your GitHub account.
2. Click on **"Generate new token"** (classic) or **"Tokens (fine-grained)"** depending on GitHub's current interface.
3. Set a **token name** (e.g., `github-api-notebook`).
4. Choose an **expiration date** (recommended: 30 or 90 days for short-term use).
5. Select the following scopes:
   - `repo` (for private repositories, if applicable)
   - `read:org` (to access organization information)
   - `read:user` (to access user details)
6. Click **Generate token**.
7. **Copy and save your token immediately**—you won’t be able to see it again later.

## Using token

All functions require a GitHub PAT (Personal Access Token) with appropriate
scopes:

```bash
export GITHUB_ACCESS_TOKEN="your_token"
```

Scopes required:

- `repo` (for private repo access)
- `read:org` (to fetch org members and repositories)

- Go to new PAT (classic) https://github.com/settings/tokens/new


# Assessing Developer Performance via GitHub API

## Introduction

The notebook `github.example.ipynb` demonstrates how to use a custom Python-based
wrapper around the GitHub API to **analyze developer activity** and
**contributions** within an organization. It provides practical tools for
engineering managers, team leads, and data analysts to measure productivity and
engagement over time.

GitHub stores a wealth of activity data such as commits, pull requests (PRs), and
issue interactions. However, extracting meaningful insights from GitHub’s native
API can be challenging due to its raw structure and pagination mechanisms. To
simplify this, we’ve built a software layer that exposes **clean**, and
**high-level functions** that return structured metrics ready for analysis.

With these APIs, you can:

- Track contributions of individual developers (commits, PRs, unmerged work).
- Compare productivity across teammates.
- Identify your most active or consistent contributors.
- Visualize patterns across repositories and timeframes.
- Support engineering OKRs, sprint planning, and retrospectives with data.

Throughout the notebook, we’ll implement real-life scenarios that use these APIs
and visualize the insights with interactive Plotly charts.

## Real-Life Use Cases

These functions are designed to support practical workflows:

- **Performance Reviews**: Use user-specific metrics to track engineering KPIs.
- **Top Contributor Reports**: Rank users based on commit/PR stats.
- **Sprint Planning**: Visualize developer throughput across projects.
- **Pull Request Hygiene**: Monitor unmerged or stale PRs to improve code review
  cycles.
- **Productivity Dashboards**: Build Streamlit or Dash apps using structured
  JSON outputs.

## Potential Applications

Our custom GitHub API layer enables a wide range of data-driven assessments of
developer activity and repository health. Below are some practical use cases that
can be directly implemented using the APIs exposed by our software layer.

### Individual Developer Contribution Report
Generate a personal activity summary for a specific contributor within a defined
time range. Metrics include:
- Number of commits across repositories.
- Number of pull requests (PRs) created.
- Count of unmerged or closed PRs.
- Issue involvement and assignments.

**Use case:** Great for quarterly reviews or self-assessments.

### Comparative Productivity Analysis
Compare the contributions of two or more developers using metrics such as:
- Commits per repository.
- PRs submitted and merged.
- Frequency of contributions.

**Use case:** Helps team leads assess team balance, recognize underappreciated
efforts, or allocate resources more efficiently.

### Identify Most Active Contributors
Scan an entire organization and rank users based on contribution statistics such as:
- Total commits.
- PR activity (opened/merged).
- Issues closed or managed.

**Use case:** Identify top performers or potential mentors in the team.

### Stale or Unmerged PR Monitoring
Detect PRs that have been closed but not merged. These could indicate:
- Abandoned or rejected work.
- PRs needing review attention.

**Use case:** Improve code review cycles and minimize wasted effort.

### Open Issues Without Assignees
Track unassigned issues to ensure tasks are distributed and prioritized appropriately.

**Use case:** Project managers can use this to ensure no work falls through the cracks.

### Team-Level Activity Heatmaps
Generate visual dashboards showing activity across teams or projects:
- Contribution volume by repository.
- Commit spikes over time.

**Use case:** Great for retrospectives, planning meetings, or engineering
leadership reports.

# GitHub API Wrapper Documentation

This document outlines the core endpoints and utility functions provided in the
`github_utils.py` module. The purpose of this wrapper is to simplify GitHub
analytics for developer performance tracking and team productivity insights.

## GitHub Endpoints Used in the Wrapper

### Commits API

- Endpoint: `GET /repos/{owner}/{repo}/commits`
  - Usage: Retrieves commits for a repository, optionally filtered by author and
    date range.

### Pull Requests API

- Endpoint: `GET /repos/{owner}/{repo}/pulls`
  - Usage: Fetches pull requests based on state (open, closed, all).
- Endpoint: `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - Usage: Fetches metadata about an individual PR, such as author and merge
    status.

### Issues API

- Endpoint: `GET /repos/{owner}/{repo}/issues`
  - Usage: Retrieves issues, optionally filtered by state and since date. Used
    for counting issues and filtering unassigned ones.

### Repositories API

- Endpoint: `GET /orgs/{org}/repos`
  - Usage: Fetches all repositories under a specific organization.

### Contributors API

- Endpoint: `GET /repos/{owner}/{repo}/contributors`
  - Usage: Returns contributors to a repository along with commit counts.

## Core Wrapper Functions

### `GitHubAPI`

Initializes an authenticated GitHub client using a personal access token (PAT).

- Automatically detects token from environment or accepts explicitly.
- Handles both public GitHub and GitHub Enterprise (custom base URL).

### `get_repo_names`

- Returns all repositories under a GitHub organization.

  **Returns**:

  ```python
  {
      "owner": "org_name",
      "repositories": ["repo1", "repo2", ...]
  }
  ```

### `get_github_contributors`

- Retrieves all contributors across a list of repositories.

  **Returns**:

  ```python
  {
      "org/repo1": ["user1", "user2", ...],
      ...
  }
  ```

### `normalize_period_to_utc`

- Converts naive or local datetime objects into UTC-aware datetimes.

## Global Metrics Functions

### `get_total_commits`

- Computes the total number of commits across all repositories in an
  organization.
- Optionally filtered by usernames and a time period.

### `get_total_prs`

- Computes the number of PRs by state (`open`, `closed`, or `all`) within an
  org.
- Optionally filtered by usernames and time period.

### `get_prs_not_merged`

- Identifies closed PRs that were never merged.

  **Use case**: Detect abandoned or rejected PRs.

### `get_total_issues`

- Retrieves issue counts across all repositories, excluding PRs.
- Allows filtering by state and time window.

### `get_issues_without_assignee`

- Returns the number of issues that have no assignee, useful for task triage.

## User-Centric Wrapper Functions

These functions wrap global metrics to return results for individual users.

### `get_commits_by_person`

- Returns total commits made by a specific GitHub user, along with repository
  breakdown.

### `get_prs_by_person`

- Returns number of PRs opened by a specific user, optionally filtered by state.

### `get_prs_not_merged_by_person`

- Returns unmerged PRs authored by a specific user.

### `get_issues_by_person`

- Returns number of issues authored by a specific user.
