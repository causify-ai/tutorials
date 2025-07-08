# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
# - [Github API to understand user Contribution](#github-api-to-understand-user-contribution)
# - [Authenticate GitHub Client](#authenticate-github-client)
# - [Define Time Period](#define-time-period)
# - [Specify Users and Repos to Fetch and Cache Data](#specify-users-and-repos-to-fetch-and-cache-data)
#   - [Pre-feth all the data you need in cache](#pre-feth-all-the-data-you-need-in-cache)
# - [Collect Daily Metrics](#collect-daily-metrics)
# - [Summarize Contributions and Visualize for Entire period that was cached](#summarize-contributions-and-visualize-for-entire-period-that-was-cached)
#   - [a. Compare users Total performance across selected repos](#a.-compare-users-total-performance-across-selected-repos)
#   - [b. Compare a users performance Individually across repos](#b.-compare-a-users-performance-individually-across-repos)
#   - [c. Compare Multiple users inside one repo](#c.-compare-multiple-users-inside-one-repo)
# - [Performance Evaluation](#performance-evaluation)

# %% [markdown]
# <a name='github-api-to-understand-user-contribution'></a>
# # Github API to understand user Contribution

# %% [markdown]
# These numbers come straight from the upstream repo via the REST API, so they only include commits and PRs where you’re the author or the committer on that repo. They **do not** pick up any work you did in a fork (or the individual commits squashed into a single merge), which is why they’ll always undercount what GitHub Insights shows for your overall contributions.
#

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim PyGithub)"
# !jupyter labextension enable

# %%
import logging
import os
import datetime
import time
import importlib 

import github_utils
import helpers.hcache_simple as hcacsimp
from github import Github

# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %%
#importlib.reload(github_utils)
# %load_ext autoreload
# %autoreload 2

# %% [markdown]
# <a name='authenticate-github-client'></a>
# # Authenticate GitHub Client

# %%
# Set your GitHub access token here.
os.environ["GITHUB_ACCESS_TOKEN"] = ""

# %%
access_token = os.getenv("GITHUB_ACCESS_TOKEN")
if not access_token:
    _LOG.error("GITHUB_ACCESS_TOKEN not set. Exiting.")
    raise ValueError("Set GITHUB_ACCESS_TOKEN environment variable")

client = github_utils.GitHubAPI(access_token=access_token).get_client()

# %%
users = github_utils.get_contributors_for_repo(client, "causify-ai", "tutorials", top_n=30)
print(users)

# %% [markdown]
# <a name='define-time-period'></a>
# # Define Time Period

# %%
# Use a long window for caching and a narrow slice for final analysis
period_full  = github_utils.utc_period("2024-01-01", "2025-06-01")
period_slice = github_utils.utc_period("2025-04-01", "2025-05-31")  

# %% [markdown]
# <a name='specify-users-and-repos-to-fetch-and-cache-data'></a>
# # Specify Users and Repos to Fetch and Cache Data

# %%
# Choose your users and repositories
users = [
    "Shaunak01", "tkpratardan", "Prahar08modi","sandeepthalapanane","indrayudd","Swapnika29","mongolianjesus","cma0416"
]
repos = ["helpers", "tutorials", "cmamp"]
org = "causify-ai"

# %% [markdown]
# <a name='pre-feth-all-the-data-you-need-in-cache'></a>
# ## Pre-feth all the data you need in cache 

# %% [markdown]
# Query extraction takes time, so prefetch all data in cache for all the users, repos and time frames you need. once in cache there are several utility functions to help understand the user contribution. Following is the data we will fetch for users in multiple repos for the given period 
# - Prs opened in the repo
# - Commits done
# - LOC [additions and deletions]

# %%
# This will call the GitHub API and write results to disk
github_utils.prefetch_periodic_user_repo_data(client, org, repos, users, period_full)


# %% [markdown]
# <a name='collect-daily-metrics'></a>
# # Collect Daily Metrics

# %%
# Merge commits, PRs, issues, and LOCs into one DataFrame
# This DataFrame has one row per (user, repo, date) with metrics: commits, PRs, issues, LOC changes
combined_df = github_utils.collect_all_metrics(client, org, repos, users, period_full)

# %% [markdown]
# <a name='summarize-contributions-and-visualize-for-entire-period-that-was-cached'></a>
# # Summarize Contributions and Visualize for Entire period that was cached

# %% [markdown]
# <a name='a.-compare-users-total-performance-across-selected-repos'></a>
# ## a. Compare users Total performance across selected repos

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df,
    metrics=["commits", "prs", "issues_closed"],
    users=["Shaunak01", "tkpratardan", "Prahar08modi", "sandeepthalapanane"],
    repos=repos,
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 5, 15),)

# %% [markdown]
# <a name='b.-compare-a-users-performance-individually-across-repos'></a>
# ## b. Compare a users performance Individually across repos

# %%
github_utils.plot_metrics_by_repo(
    combined=combined_df,
    user="tkpratardan",
    metrics=["commits", "prs", "issues_closed"],
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 5, 15),
)

# %% [markdown]
# <a name='c.-compare-multiple-users-inside-one-repo'></a>
# ## c. Compare Multiple users inside one repo

# %%
github_utils.plot_metrics_by_user(
    combined=combined_df,
    repo="cmamp",
    users=["tkpratardan", "Shaunak01", "Prahar08modi"],
    metrics=["commits", "prs", "issues_closed"],
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 5, 15),
)


# %% [markdown]
# <a name='performance-evaluation'></a>
# # Performance Evaluation

# %%
# Step 0: Define your slice
users = ["Shaunak01", "tkpratardan", "Prahar08modi", "sandeepthalapanane"]
repos = ["cmamp", "helpers"]
metrics = ["commits", "prs", "issues_closed"]

# Step 1: Summarize total metrics across users/repos
summary_users = github_utils.summarize_users_across_repos(combined_df, users=users, repos=repos)

# Step 2: Add z-scores and percentiles
z_df  = github_utils.compute_z_scores(summary_users, metrics)
stats = github_utils.compute_percentile_ranks(z_df, metrics)

# Step 3: Visualize — will automatically pick up all *_z or *_pctile columns
github_utils.visualize_user_metric_comparison(stats, score_type="z")
github_utils.visualize_user_metric_comparison(stats, score_type="percentile")


# %% [markdown]
# There are many more helper funcs to see and compare statistics. Look at github_utils for more info -> `tutorial_github_causify_style/github_utils.py`
