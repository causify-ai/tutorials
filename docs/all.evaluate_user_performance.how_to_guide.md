<!-- toc -->

- [Developer Performance Evaluation Toolkit](#developer-performance-evaluation-toolkit)
  * [Architectural Overview](#architectural-overview)
  * [Setup](#setup)
    + [Define a UTC period](#define-a-utc-period)
    + [Prefetch and cache all activity](#prefetch-and-cache-all-activity)
  * [Collecting Metrics](#collecting-metrics)
    + [Collect daily activity for every user–repo pair](#collect-daily-activity-for-every-user%E2%80%93repo-pair)
  * [Visualization](#visualization)
    + [Compare one user across repositories](#compare-one-user-across-repositories)
    + [Compare users within one repository](#compare-users-within-one-repository)
    + [Multi-metric comparison across users](#multi-metric-comparison-across-users)
  * [Benchmarking](#benchmarking)
    + [Z-scores (standard deviations from group mean)](#z-scores-standard-deviations-from-group-mean)
    + [Percentile ranks (0–1 scale)](#percentile-ranks-0%E2%80%931-scale)
  * [Utility Functions](#utility-functions)
  * [Function Index (Quick Reference)](#function-index-quick-reference)
  * [Why Caching Matters](#why-caching-matters)

<!-- tocstop -->

# Developer Performance Evaluation Toolkit

- This toolkit collects and analyzes GitHub activity (commits, PRs, LOC, issues)
  for a set of users and repositories over a chosen time window
- The GitHub utils code is located at
  [`/tutorial_github_causify_style/github_utils.py`](/tutorial_github_causify_style/github_utils.py)

## Architectural Overview

- One-time data download
  - We fetch all activity for the full analysis window and cache it on disk
    (as JSON file)
  - Subsequent analyses reuse that cached data, so we never re-hit the GitHub
    API unless you extend the time window or explicitly clear the cache
  - This avoids rate limits and long network waits
- Daily aggregation
  - Raw commit / PR / issue timestamps are converted into per-day counts
  - LOC stats are summed per day, with additions as "+" and deletions as "−"
- Flexible slicing
  - After caching, any shorter sub-period can be filtered in memory with no
    extra API calls
- Summary and plotting layers
  - Summaries collapse daily data into totals by user, by repo, or by user–repo
    pairs
  - Plot helpers generate grouped bar charts for quick visual insight
- Benchmarking utilities
  - Z-scores and percentile ranks quantify how each user compares to the
    selectable group of peers

## Setup

### Define a UTC period

- Convert two ISO date strings to timezone-aware datetime objects:
  ```bash
  period = github_utils.utc_period("2025-01-01", "2025-05-24")
  ```

### Prefetch and cache all activity

- The following call:
  - Iterates over every (user, repo) pair
  - Fetches commits, PRs, LOC, and issues once
  - Writes them to JSON cache files

  ```bash
  github_utils.prefetch_periodic_user_repo_data(
      client,
      org="causify-ai",
      repos=["helpers", "tutorials", "cmamp"],
      users=["Shaunak01", "tkpratardan", "Prahar08modi"],
      period=period,
  )
  ```

- Progress is tracked with a `tqdm` progress bar

- The decorator `@simple_cache` keys each API result by function name and
  arguments and writes through to disk `cache.\*.json`
  - Future calls with the same arguments are cache hits

- The stats are collected only for the upstream repo, so they only include
  commits and PRs on `master`
  - They do not pick up any work you did in a fork (or the individual commits
    squashed into a single merge)
  - For this reason they undercount what GitHub Insights shows for your overall
    contributions

## Collecting Metrics

### Collect daily activity for every user–repo pair

```bash
combined = github_utils.collect_all_metrics(
    client,
    org="causify-ai",
    repos=["helpers", "tutorials", "cmamp"],
    users=["Shaunak01", "tkpratardan", "Prahar08modi"],
    period=period,
)
```

- The function builds a DataFrame of daily counts across `commits`, `PRs`,
  `LOC`, and `issues`
- Each row corresponds to one day of activity for one user in one repo
- Columns include `date`, `commits`, `prs`, `additions`, `deletions`,
  `issues_assigned`, `issues_closed`, `repo`, and `user`

## Visualization

### Compare one user across repositories

```bash
github_utils.plot_metrics_by_repo(
    combined,
    user="Shaunak01",
    start=datetime.datetime(2025, 3, 1, tzinfo=datetime.timezone.utc),
    end=datetime.datetime(2025, 5, 1, tzinfo=datetime.timezone.utc),
    metrics=["commits", "prs"],
)
```

### Compare users within one repository

```bash
github_utils.plot_metrics_by_user(
    combined,
    repo="helpers",
    start=datetime.datetime(2025, 3, 1, tzinfo=datetime.timezone.utc),
    end=datetime.datetime(2025, 5, 1, tzinfo=datetime.timezone.utc),
    metrics=["commits", "prs"],
)
```

### Multi-metric comparison across users

```python
github_utils.plot_multi_metrics_totals_by_user(
    combined,
    metrics=["commits", "prs", "additions", "issues_closed"],
    start=datetime.datetime(2025, 3, 1, tzinfo=datetime.timezone.utc),
    end=datetime.datetime(2025, 5, 1, tzinfo=datetime.timezone.utc),
    users=["Shaunak01", "tkpratardan", "Prahar08modi"],
    repos=["helpers", "tutorials", "cmamp"],
)
```

- The plots automatically summarize and filter the data over the chosen time
  window
- No need to slice or group manually, just pass the raw combined data

## Benchmarking

### Z-scores (standard deviations from group mean)

- Before computing benchmarks, use `summarize_users_across_repos()` to aggregate
  total metrics per user across selected repos

  ```python
  summary = github_utils.summarize_users_across_repos(
      combined,
      users=["Shaunak01", "tkpratardan", "Prahar08modi"],
      repos=["helpers", "tutorials", "cmamp"],
  )

  z_df = github_utils.compute_z_scores(
      summary,
      metrics=["commits", "prs", "additions"],
  )
  ```

### Percentile ranks (0–1 scale)

```bash
pct_df = github_utils.compute_percentile_ranks(
    summary,
    metrics=["commits", "prs", "additions"],
)
```

- Both functions append new columns (e.g., commits_z, commits_pctile) to the
  input DataFrame.

## Utility Functions

| Function                      | Purpose                                             |
| ----------------------------- | --------------------------------------------------- |
| `utc_period()`                | Produce a `(start_dt, end_dt)` tuple in UTC         |
| `slice_period()`              | Filter a DataFrame by the `date` column             |
| `get_contributors_for_repo()` | Retrieve top N committers to a GitHub repository    |
| `days_between()`              | Generate a list of all calendar days in a time span |

## Function Index (Quick Reference)

| Layer              | Key Functions                                                                                                                                                                                                       | Responsibility                                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Data Fetch + Cache | `get_commit_datetimes_by_repo_period_intrinsic`, `get_pr_datetimes_by_repo_period_intrinsic`, `get_issue_datetimes_by_repo_intrinsic`, `get_loc_stats_by_repo_period_intrinsic`, `prefetch_periodic_user_repo_data` | Hit GitHub API once and write to JSON cache    |
| Daily Aggregation  | `build_daily_commit_df`, `build_daily_pr_df`, `build_daily_issue_df`, `build_daily_loc_df`                                                                                                                          | Convert raw timestamps to per-day counts       |
| Collection         | `collect_all_metrics`                                                                                                                                                                                               | Merge all daily metrics into one DataFrame     |
| Summaries          | `summarize_user_metrics_for_repo`, `summarize_repo_metrics_for_user`, `summarize_users_across_repos`                                                                                                                | Aggregate totals by user or repo               |
| Visualization      | `plot_metrics_by_repo`, `plot_metrics_by_user`, `plot_multi_metrics_totals_by_user`                                                                                                                                 | Produce grouped bar charts for visual analysis |
| Benchmarking       | `compute_z_scores`, `compute_percentile_ranks`                                                                                                                                                                      | Compare user performance against the group     |

## Why Caching Matters

Fetching commit history and issue events from GitHub can be slow especially
across many users and repositories. By decorating the raw fetch functions with
`@simple_cache(write_through=True)`:

- First run writes each query to a disk cach.
- Subsequent runs read instantly from disk.
- Analysis and plotting operate entirely on local DataFrames.

This design removes API latency from interactive analysis while keeping data
fresh whenever you extend the time window or force a cache refresh.
