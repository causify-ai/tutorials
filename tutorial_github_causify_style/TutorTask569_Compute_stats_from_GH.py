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
# - [Compute stats for Team members](#compute-stats-for-team-members)
#   - [Authenticate GitHub Client](#authenticate-github-client)
#   - [Define Time Period](#define-time-period)
#   - [Pre-feth all the data you need in cache](#pre-feth-all-the-data-you-need-in-cache)
#   - [Collect Daily Metrics](#collect-daily-metrics)
#   - [a. Compare users Total performance across all repos since last 3 months](#a.-compare-users-total-performance-across-all-repos-since-last-3-months)
#   - [Performance Evaluation](#performance-evaluation)

# %% [markdown]
# <a name='compute-stats-for-team-members'></a>
# # Compute stats for Team members

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim PyGithub)"
# !jupyter labextension enable

# %%
import datetime
import logging
import os

import github_utils

# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %%
# importlib.reload(github_utils)
# %load_ext autoreload
# %autoreload 2

# %% [markdown]
# <a name='authenticate-github-client'></a>
# ## Authenticate GitHub Client

# %%
os.environ["GITHUB_ACCESS_TOKEN"] = ""

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
users_cmamp = [
    "gpsaggese",
    "gitpaulsmith",
    "rheenina",
    "DanilYachmenev",
    "jsmerix",
    "PomazkinG",
    "tamriq",
    "mongolianjesus",
    "dremdem",
    "Sameep2808",
    "Shayawnn",
    "sonniki",
    "samarth9008",
    "heanhsok",
    "Vedanshu7",
    "pavolrabatin",
    "amrawadk",
    "Shaunak01",
    "Jd8111997",
    "tkpratardan",
    "cma0416",
]

# %% [markdown]
# <a name='define-time-period'></a>
# ## Define Time Period

# %%
# Use a long window for caching and a narrow slice for final analysis
period_full = github_utils.utc_period("2025-01-01", "2025-06-23")
# period_slice = github_utils.utc_period("2025-04-01", "2025-05-31")

# %% [markdown]
# <a name='pre-feth-all-the-data-you-need-in-cache'></a>
# ## Pre-feth all the data you need in cache

# %%
repos = [
    "helpers",
    "tutorials",
    "cmamp",
    "kaizenflow",
    "orange",
    "sports_analytics",
]
org = "causify-ai"

# %%
github_utils.prefetch_periodic_user_repo_data(
    client, org, repos, users_cmamp, period_full
)

# %% [markdown]
# <a name='collect-daily-metrics'></a>
# ## Collect Daily Metrics

# %%
combined_df = github_utils.collect_all_metrics(
    client, org, repos, users_cmamp, period_full
)

# %% [markdown]
# <a name='a.-compare-users-total-performance-across-all-repos-since-last-3-months'></a>
# ## a. Compare users Total performance across all repos since last 3 months

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df,
    metrics=["prs", "issues_closed"],
    users=users_cmamp,
    repos=repos,
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 6, 23),
)

# %% [markdown]
# <a name='performance-evaluation'></a>
# ## Performance Evaluation

# %%
# Step 0: Define your slice
users = users_cmamp
repos = repos
metrics = ["prs", "issues_closed"]

# Step 1: Summarize total metrics across users/repos
summary_users = github_utils.summarize_users_across_repos(
    combined_df, users=users, repos=repos
)

# Step 2: Add z-scores and percentiles
z_df = github_utils.compute_z_scores(summary_users, metrics)
stats = github_utils.compute_percentile_ranks(z_df, metrics)

# Step 3: Visualize — will automatically pick up all *_z or *_pctile columns
github_utils.visualize_user_metric_comparison(stats, score_type="z")
github_utils.visualize_user_metric_comparison(stats, score_type="percentile")
