# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
# - [Imports](#imports)
# - [Authenticate GitHub Client](#authenticate-github-client)
# - [Pre-feth all the data from Jan 2025 in cache](#pre-feth-all-the-data-from-jan-2025-in-cache)
# - [Full Time Evaluation](#full-time-evaluation)
# - [Compare Full time contributors total performance across all repos since last 1 months](#compare-full-time-contributors-total-performance-across-all-repos-since-last-1-months)
# - [Performance Evaluation - FullTime - Last 1 Months (based on Issues and PRs closed)](#performance-evaluation---fulltime---last-1-months-(based-on-issues-and-prs-closed))
# - [Compare Full time contributors total performance across all repos since last 3 months](#compare-full-time-contributors-total-performance-across-all-repos-since-last-3-months)
# - [Performance Evaluation - FullTime - Last 3 Months (based on Issues and PRs closed)](#performance-evaluation---fulltime---last-3-months-(based-on-issues-and-prs-closed))
# - [Compare Full time contributors total performance across all repos since last Jan 2025](#compare-full-time-contributors-total-performance-across-all-repos-since-last-jan-2025)
# - [Performance Evaluation - FullTime - Since Jan 2025 (based on Issues and PRs closed)](#performance-evaluation---fulltime---since-jan-2025-(based-on-issues-and-prs-closed))

# %% [markdown]
# <a name='imports'></a>
# # Imports

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim PyGithub)"
# !jupyter labextension enable

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import datetime
import logging
import os

import github_utils

# %%
# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %% [markdown]
# <a name='authenticate-github-client'></a>
# # Authenticate GitHub Client

# %%
os.environ["GITHUB_ACCESS_TOKEN"] = "*"

# %%
access_token = os.getenv("GITHUB_ACCESS_TOKEN")
if not access_token:
    _LOG.error("GITHUB_ACCESS_TOKEN not set. Exiting.")
    raise ValueError("Set GITHUB_ACCESS_TOKEN environment variable")
client = github_utils.GitHubAPI(access_token=access_token).get_client()

# %%
users = github_utils.get_github_contributors(
    client, repo_names=["causify-ai/cmamp"]
)
print(users)

# %%
active_users_total = [
    "gpsaggese",
    "tkpratardan",
    "Shaunak01",
    "sonniki",
    "heanhsok",
    "Shayawnn",
    "rheenina",
    "PomazkinG",
    "gitpaulsmith",
    "samarth9008",
    "Vedanshu7",
    "dremdem",
    "cma0416",
    "tamriq",
    "mongolianjesus",
    "DanilYachmenev",
]

# %% [markdown]
# <a name='pre-feth-all-the-data-from-jan-2025-in-cache'></a>
# # Pre-feth all the data from Jan 2025 in cache

# %%
# Use a long window for caching and a narrow slice for final analysis.
period_full = github_utils.utc_period("2025-01-01", "2025-10-01")

# %%
repos = [
    "helpers",
    "tutorials",
    "cmamp",
    "kaizenflow",
    "orange",
    "sports_analytics",
    "csfy",
]
org = "causify-ai"

# %%
github_utils.prefetch_periodic_user_repo_data(
    client, org, repos, active_users_total, period_full
)

# %% [markdown]
# <a name='full-time-evaluation'></a>
# # Full Time Evaluation

# %%
combined_df_fulltime = github_utils.collect_all_metrics(
    client, org, repos, active_users_total, period_full
)

# %%
if "issue_comments" not in combined_df_fulltime.columns:
    combined_df_fulltime["issue_comments"] = 0
if "pr_reviews" not in combined_df_fulltime.columns:
    combined_df_fulltime["pr_reviews"] = 0

# %% [markdown]
# <a name='compare-full-time-contributors-total-performance-across-all-repos-since-last-1-months'></a>
# # Compare Full time contributors total performance across all repos since last 1 months

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["prs", "issues_closed", "issues_assigned"],
    users=active_users_total,
    repos=repos,
    start=datetime.datetime(2025, 9, 1),
    end=datetime.datetime(2025, 10, 1),
)

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["additions", "deletions"],
    users=[u for u in active_users_total if u != "gpsaggese"],
    repos=repos,
    start=datetime.datetime(2025, 9, 1),
    end=datetime.datetime(2025, 10, 1),
)

# %% [markdown]
# <a name='performance-evaluation---fulltime---last-1-months-(based-on-issues-and-prs-closed)'></a>
# # Performance Evaluation - FullTime - Last 1 Months (based on Issues and PRs closed)

# %%
combined_df_fulltime_1 = github_utils.slice_by_date(
    combined_df_fulltime, "2025. 9, 1", "2025, 10, 1"
)
metrics = ["prs", "issues_closed"]
summary_users_fulltime = github_utils.summarize_users_across_repos(
    combined_df_fulltime_1, users=active_users_total, repos=repos
)
stats = github_utils.compute_percentile_ranks(summary_users_fulltime, metrics)
github_utils.visualize_user_metric_comparison(
    stats, score_type="percentile", top_n=10
)

# %% [markdown]
# <a name='compare-full-time-contributors-total-performance-across-all-repos-since-last-3-months'></a>
# # Compare Full time contributors total performance across all repos since last 3 months

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["prs", "issues_closed", "issues_assigned"],
    users=active_users_total,
    repos=repos,
    start=datetime.datetime(2025, 7, 1),
    end=datetime.datetime(2025, 10, 1),
)

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["additions", "deletions"],
    users=active_users_total,
    repos=repos,
    start=datetime.datetime(2025, 7, 1),
    end=datetime.datetime(2025, 10, 1),
)

# %% [markdown]
# <a name='performance-evaluation---fulltime---last-3-months-(based-on-issues-and-prs-closed)'></a>
# # Performance Evaluation - FullTime - Last 3 Months (based on Issues and PRs closed)

# %%
combined_df_fulltime_3 = github_utils.slice_by_date(
    combined_df_fulltime, "2025. 7, 1", "2025, 10, 1"
)
metrics = ["prs", "issues_closed"]
summary_users_fulltime_3 = github_utils.summarize_users_across_repos(
    combined_df_fulltime_3, users=active_users_total, repos=repos
)
stats_3 = github_utils.compute_percentile_ranks(summary_users_fulltime_3, metrics)
github_utils.visualize_user_metric_comparison(
    stats_3, score_type="percentile", top_n=10
)

# %% [markdown]
# <a name='compare-full-time-contributors-total-performance-across-all-repos-since-last-jan-2025'></a>
# # Compare Full time contributors total performance across all repos since last Jan 2025

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["prs", "issues_closed", "issues_assigned"],
    users=active_users_total,
    repos=repos,
    start=datetime.datetime(2025, 1, 1),
    end=datetime.datetime(2025, 10, 1),
)

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["additions", "deletions"],
    users=active_users_total,
    repos=repos,
    start=datetime.datetime(2025, 1, 1),
    end=datetime.datetime(2025, 10, 1),
)

# %% [markdown]
# <a name='performance-evaluation---fulltime---since-jan-2025-(based-on-issues-and-prs-closed)'></a>
# # Performance Evaluation - FullTime - Since Jan 2025 (based on Issues and PRs closed)

# %%
combined_df_fulltime_jan = github_utils.slice_by_date(
    combined_df_fulltime, "2025, 1, 1", "2025, 10, 1"
)
metrics = ["prs", "issues_closed"]
summary_users_fulltime_jan = github_utils.summarize_users_across_repos(
    combined_df_fulltime_jan, users=active_users_total, repos=repos
)
stats_jan = github_utils.compute_percentile_ranks(
    summary_users_fulltime_jan, metrics
)
github_utils.visualize_user_metric_comparison(
    stats_jan, score_type="percentile", top_n=10
)
