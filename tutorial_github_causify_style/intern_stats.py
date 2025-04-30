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
    "end_date": (datetime(2025, 4, 28)),
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

# Initialize results container and tracking
comparison_results = []
completed_users = set()

# Helper to wait for rate limit reset
def wait_for_rate_limit_reset(client):
    rate_limit = client.get_rate_limit()
    remaining = rate_limit.core.remaining
    reset_timestamp = rate_limit.core.reset.timestamp()
    current_timestamp = datetime.now(timezone.utc).timestamp()

    if remaining == 0:
        sleep_time = reset_timestamp - current_timestamp
        if sleep_time > 0:
            print(f"[Rate Limit Hit] Sleeping for {sleep_time/60:.2f} minutes...")
            time.sleep(sleep_time + 5)  # Add 5 seconds buffer

# Loop until all usernames are processed
pending_usernames = usernames.copy()

while pending_usernames:
    username = pending_usernames[0]
    try:
        print(f"Processing user: {username}")

        wait_for_rate_limit_reset(client)  # Check before calling
        commits_data = github_utils.get_commits_by_person(
            client, username, config["org_name"],
            period=(config["start_date"], config["end_date"]),
            repo_names=repos
        )

        wait_for_rate_limit_reset(client)  # Check again
        
        prs_data = github_utils.get_prs_by_person(
            client, username, config["org_name"],
            period=(config["start_date"], config["end_date"]),
            state="all",
            repo_names=repos
        )

        # Initialize values
        total_commits = commits_data["total_commits"]
        total_additions = 0
        total_deletions = 0
        repo_breakdown = {}

        for repo, branches in commits_data["commits_per_repository"].items():
            repo_additions = 0
            repo_deletions = 0
            repo_commits = 0
            repo_master_commits = 0

            for branch, stats in branches.items():
                repo_additions += stats["additions"]
                repo_deletions += stats["deletions"]
                repo_commits += stats["commits"]

                if branch == "master":
                    repo_master_commits = stats["commits"]

            repo_breakdown[repo] = {
                "repo_commits": repo_commits,
                "repo_master_commits": repo_master_commits,
                "repo_additions": repo_additions,
                "repo_deletions": repo_deletions,
                "repo_total_changes": repo_additions + repo_deletions
            }

            total_additions += repo_additions
            total_deletions += repo_deletions
        
        comparison_results.append({
            "Username": username,
            "Total Commits": total_commits,
            "Total PRs": prs_data["total_prs"],
            "Total Additions": total_additions,
            "Total Deletions": total_deletions,
            "Total Changes": total_additions + total_deletions,
            "Repo Breakdown": repo_breakdown,
        })

        pending_usernames.pop(0)  # Pop the first user
        completed_users.add(username)
        print(f"Finished processing user: {username}")

    except Exception as e:
        print(f"Error occurred while processing user {username}: {e}")
        print("Will retry after rate limit reset...")
        pending_usernames.insert(0, username)  # Retry this user later

        # Wait for rate limit reset before trying again
        wait_for_rate_limit_reset(client)

# Finally create dataframe
df_comparison = pd.DataFrame(comparison_results)
df_comparison

# %%
# Define developer GitHub usernames.
usernames = ["aangelo9", "allenmatt10", "indrayudd", "neomisule", "Peeyush4", "sandeepthalapanane"]

# Define Repositories to search
repos = ["helpers", "tutorials"]

# Initialize results container.
comparison_results = []

# Collect metrics for each user.
for username in usernames:
    commits_data = github_utils.get_commits_by_person(
        client, username, config["org_name"],
        period=(config["start_date"], config["end_date"]),
        repo_names=repos
    )
    prs_data = github_utils.get_prs_by_person(
        client, username, config["org_name"],
        period=(config["start_date"], config["end_date"]),
        state="all",
        repo_names=repos
    )

    # Initialize values
    total_commits = commits_data["total_commits"]
    commits_to_master = 0
    total_additions = 0
    total_deletions = 0
    repo_breakdown = {}

    # Loop through each repo and branch inside commits_per_repository
    for repo, branches in commits_data["commits_per_repository"].items():
        repo_additions = 0
        repo_deletions = 0
        repo_commits = 0
        repo_master_commits = 0

        for branch, stats in branches.items():
            repo_additions += stats["additions"]
            repo_deletions += stats["deletions"]
            repo_commits += stats["commits"]

            if branch == "master":
                repo_master_commits = stats["commits"]

        repo_breakdown[repo] = {
            "repo_commits": repo_commits,
            "repo_master_commits": repo_master_commits,
            "repo_additions": repo_additions,
            "repo_deletions": repo_deletions,
            "repo_total_changes": repo_additions + repo_deletions
        }

        total_additions += repo_additions
        total_deletions += repo_deletions
    
    comparison_results.append({
        "Username": username,
        "Total Commits": total_commits,
        "Total PRs": prs_data["total_prs"],
        "Total Additions": total_additions,
        "Total Deletions": total_deletions,
        "Total Changes": total_additions + total_deletions,
        "Repo Breakdown": repo_breakdown,
    })

# Create DataFrame.
df_comparison = pd.DataFrame(comparison_results)
df_comparison

# %%
# Expand Repo Breakdown into a new flat dataframe
repo_master_commit_records = []

for _, row in df_comparison.iterrows():
    username = row["Username"]
    repo_breakdown = row["Repo Breakdown"]
    for repo_name, repo_stats in repo_breakdown.items():
        repo_master_commit_records.append({
            "Username": username,
            "Repository": repo_name,
            "Commits to Master": repo_stats.get("repo_master_commits", 0)
        })

# Create a flat DataFrame
df_master_commits = pd.DataFrame(repo_master_commit_records)

# Only keep rows where there are actually master commits (optional filtering)
df_master_commits = df_master_commits[df_master_commits["Commits to Master"] > 0]

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

# Commits to master branch
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

# Total Line changes
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
