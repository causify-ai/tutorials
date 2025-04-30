# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Comparing Performances for the Interns
#
# In this notebook, we will compare six developers' performance based on:
# - Total commits made
# - Number of PRs opened
# - Number of PRs closed but not merged
#
# The results will be displayed using interactive Plotly bar charts.

# %% [markdown]
# ## Setup
#
# Before proceeding with API calls, ensure that your environment is correctly set up.

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# !jupyter labextension enable

# %% [markdown]
# ### Install required libraries
# Install the required libraries: 

# %%
# Install plotly.
# !sudo /venv/bin/pip install plotly

# %% [markdown]
# ### Import Required Modules
# Import the necessary libraries:

# %%
import os
import logging
import github_utils
import pandas as pd
import time
from github import Github
from datetime import datetime, timedelta, timezone
import plotly.express as px
from itertools import chain

# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %% [markdown]
# ### Set Up GitHub Authentication
# Store your **GitHub Personal Access Token (PAT)** as an environment variable for security. You can do this in your terminal:
#
# ```sh
# export GITHUB_ACCESS_TOKEN="your_personal_access_token"
# ```
#
# Alternatively, you can set it within the notebook:

# %%
# Set your GitHub access token here.
os.environ["GITHUB_ACCESS_TOKEN"] = ""

# Retrieve it when needed.
access_token = os.getenv("GITHUB_ACCESS_TOKEN")

# Ensure the token is set correctly.
if not access_token:
    raise ValueError("GitHub Access Token is not set. Please configure it before proceeding.")

# %% [markdown]
# Now, you're ready to interact with the GitHub API!
#
# ## Define Config
# Here we define all parameters in a single `config` dictionary.
# You can easily modify:
# - The `org_name` to analyze a different GitHub organization.
# - The `start_date` and `end_date` to change the timeframe.

# %%
# Define the configuration settings.
config = {
    # Replace with actual GitHub organization or username.
    "org_name": "causify-ai",  
    "start_date": (datetime(2025, 2, 1)),
    "end_date": (datetime(2025, 4, 29)),
    # Load from environment variable.
    "access_token": access_token,  
}

# %% [markdown]
# ## Initialize GitHub Client

# %%
# Initialize the GitHub client using the access token from the config.
client = Github(config["access_token"])

# Verify authentication by retrieving the authenticated user.
try:
    authenticated_user = client.get_user().login
    print(f"Successfully authenticated as: {authenticated_user}")
except Exception as e:
    print(f"Authentication failed: {e}")

# %% [markdown]
# ## Comparing the Performances

# %%
# Define developer GitHub usernames.
usernames = ["aangelo9", "allenmatt10", "indrayudd", "neomisule", "Peeyush4", "sandeepthalapanane"]

# Define Repositories to search
repos = ["helpers", "tutorials"]

results = github_utils.collect_user_statistics(
    client=client,
    usernames=usernames,
    org_name=config["org_name"],
    period=(config["start_date"], config["end_date"]),
    repo_names=repos
)

df_comparison = pd.DataFrame(results)
df_comparison

# %%
df_master_commits = github_utils.extract_commits_to_master(df_comparison)
df_master_commits

# %% [markdown]
# ## Visualization

# %%
# Commits Comparison.
fig_total_commits = px.bar(
    df_comparison, x="Username", y="Total Commits",
    title="Total Commits per Developer",
    text="Total Commits", color="Username"
)
fig_total_commits.show()

# Commits to master branch.
fig = px.bar(
    df_master_commits,
    x="Username",
    y="Commits to Master",
    color="Repository",
    barmode="group",
    title="Commits to Master Branch per Repository by Developer",
    text="Commits to Master"
)
fig.show()

# Total Line changes.
fig_total_changes = px.bar(
    df_comparison, x="Username", y="Total Changes",
    title="Total Lines Changed per Developer",
    text="Total Changes", color="Username"
)
fig_total_changes.show()

# PRs Comparison.
fig_prs = px.bar(
    df_comparison, x="Username", y="Total PRs",
    title="Total PRs per Developer",
    text="Total PRs", color="Username"
)
fig_prs.show()
