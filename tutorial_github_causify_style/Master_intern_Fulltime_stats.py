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
# - [Pre-feth all the data from last 6 months in cache](#pre-feth-all-the-data-from-last-6-months-in-cache)
# - [Intern Evaluation](#intern-evaluation)
#   - [Compare Intern Total performance across all repos since last 3 months](#compare-intern-total-performance-across-all-repos-since-last-3-months)
#   - [Performance Evaluation - Intern - Last 3 Months (based on Issues and PRs closed)](#performance-evaluation---intern---last-3-months-(based-on-issues-and-prs-closed))
# - [Full Time Evaluation](#full-time-evaluation)
#   - [Compare Full time contributors total performance across all repos since last 3 months](#compare-full-time-contributors-total-performance-across-all-repos-since-last-3-months)
#   - [Performance Evaluation - FullTime - Last 3 Months (based on Issues and PRs closed)](#performance-evaluation---fulltime---last-3-months-(based-on-issues-and-prs-closed))

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
    "aangelo9",
    "indrayudd",
    "aver81",
    "madhurlak0810",
    "PranavShashidhara",
    "srinivassaitangudu",
    "sandeepthalapanane",
]


# %% [markdown]
# <a name='pre-feth-all-the-data-from-last-6-months-in-cache'></a>
# # Pre-feth all the data from last 6 months in cache

# %%
# Use a long window for caching and a narrow slice for final analysis.
period_full = github_utils.utc_period("2025-01-01", "2025-07-14")

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
    client, org, repos, active_users_total, period_full
)

# %%
full_time_users = [
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
]


# %%
intern_users = [
    "aangelo9",
    "indrayudd",
    "aver81",
    "madhurlak0810",
    "PranavShashidhara",
    "srinivassaitangudu",
    "sandeepthalapanane",
]


# %% [markdown]
# <a name='intern-evaluation'></a>
# # Intern Evaluation

# %%
combined_df_intern = github_utils.collect_all_metrics(
    client, org, repos, intern_users, period_full
)

# %% [markdown]
# <a name='compare-intern-total-performance-across-all-repos-since-last-3-months'></a>
# ## Compare Intern Total performance across all repos since last 3 months

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_intern,
    metrics=["prs", "issues_closed"],
    users=intern_users,
    repos=repos,
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 7, 14),
)

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_intern,
    metrics=["additions", "deletions"],
    users=intern_users,
    repos=repos,
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 7, 14),
)

# %% [markdown]
# <a name='performance-evaluation---intern---last-3-months-(based-on-issues-and-prs-closed)'></a>
# <a name='performance-evaluation---intern---last-3-months-(based-on-issues-and-prs-closed-and-)'></a>
# ## Performance Evaluation - Intern - Last 3 Months (based on Issues and PRs closed)

# %%
metrics = ["prs", "issues_closed"]
summary_users = github_utils.summarize_users_across_repos(
    combined_df_intern, users=intern_users, repos=repos
)
stats = github_utils.compute_percentile_ranks(summary_users, metrics)
github_utils.visualize_user_metric_comparison(stats, score_type="percentile")

# %% [markdown]
# <a name='full-time-evaluation'></a>
# # Full Time Evaluation

# %%
combined_df_fulltime = github_utils.collect_all_metrics(
    client, org, repos, full_time_users, period_full
)

# %% [markdown]
# <a name='compare-full-time-contributors-total-performance-across-all-repos-since-last-3-months'></a>
# ## Compare Full time contributors total performance across all repos since last 3 months

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["prs", "issues_closed"],
    users=full_time_users,
    repos=repos,
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 7, 14),
)

# %%
github_utils.plot_multi_metrics_totals_by_user(
    combined=combined_df_fulltime,
    metrics=["additions", "deletions"],
    users=full_time_users,
    repos=repos,
    start=datetime.datetime(2025, 3, 1),
    end=datetime.datetime(2025, 7, 14),
)

# %% [markdown]
# <a name='performance-evaluation---fulltime---last-3-months-(based-on-issues-and-prs-closed)'></a>
# <a name='performance-evaluation---fulltime---last-3-months-(based-on-issues-and-prs-closed-and-)'></a>
# ## Performance Evaluation - FullTime - Last 3 Months (based on Issues and PRs closed)

# %%
metrics = ["prs", "issues_closed"]
summary_users_fulltime = github_utils.summarize_users_across_repos(
    combined_df_fulltime, users=full_time_users, repos=repos
)
stats = github_utils.compute_percentile_ranks(summary_users_fulltime, metrics)
github_utils.visualize_user_metric_comparison(
    stats, score_type="percentile", top_n=10
)
