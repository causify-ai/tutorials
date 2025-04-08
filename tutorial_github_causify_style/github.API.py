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
# # GitHub API Tutorial
#
# **Overview:**
# In this notebook you'll learn how to:
# - Connect to the GitHub API using a Python client.
# - Retrieve valuable repository insights such as commit history, pull request statistics, and contributor details.
# - Perform analytics on repository activity over a given time frame.
#
# **Why Use This Notebook?**
# - Automate repository monitoring for contributions and updates.
# - Gain insights into open, closed, and unmerged pull requests.
# - Track commit frequency and user contributions.
#
# **Requirements:**
#
# To authenticate and interact with the GitHub API, you’ll need a **Personal Access Token** with appropriate scopes (permissions). Follow the steps below to generate one:
#
# 1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens) while logged into your GitHub account.
# 2. Click on **"Generate new token"** (classic) or **"Tokens (fine-grained)"** depending on GitHub's current interface.
# 3. Set a **token name** (e.g., `github-api-notebook`).
# 4. Choose an **expiration date** (recommended: 30 or 90 days for short-term use).
# 5. Select the following scopes:
#    - `repo` (for private repositories, if applicable)
#    - `read:org` (to access organization information)
#    - `read:user` (to access user details)
# 6. Click **Generate token**.
# 7. **Copy and save your token immediately**—you won’t be able to see it again later.

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# !jupyter labextension enable

# %% [markdown]
# ## Setup
#
# Before proceeding with API calls, ensure that your environment is correctly set up.

# %% [markdown]
# ### 2. Import Required Modules
# Import the necessary libraries:

# %%
import os
import logging
import github_utils
import pandas as pd
from github import Github
from datetime import datetime, timedelta

# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %% [markdown]
# ### 3. Set Up GitHub Authentication
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

# %%
# Retrieve it when needed.
access_token = os.getenv("GITHUB_ACCESS_TOKEN")

# Ensure the token is set correctly.
if not access_token:
    raise ValueError("GitHub Access Token is not set. Please configure it before proceeding.")

# %% [markdown]
# Now, you're ready to interact with the GitHub API!

# %% [markdown]
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
    "start_date": (datetime(2025, 1, 20)),
    "end_date": (datetime(2025, 2, 25)),
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
# ## Fetch Repositories for the Organization
#
# The `get_repo_names` function retrieves all repositories within a specified GitHub organization. This helps in identifying available repositories before analyzing commits or pull requests.

# %%
repos_info = github_utils.get_repo_names(client, config["org_name"])
repos_info

# %% [markdown]
# ## Fetch Commit Statistics
#
# The `get_total_commits` function allows us to retrieve the number of commits made in the repositories of a specified GitHub organization. 
#
# ### **Usage**
# - You can fetch **all commits** made during a specific time range.
# - Additionally, you can **filter commits by specific users** to analyze individual contributions.
#
# ### **Parameters**
# - `client` (*Github*): The authenticated GitHub API client.
# - `org_name` (*str*): The GitHub organization name.
# - `period` (*Optional[Tuple[datetime, datetime]]*): A tuple containing `start_date` and `end_date`.
# - `usernames` (*Optional[List[str]]*): A list of GitHub usernames to filter commits by specific users.

# %%
commit_stats = github_utils.get_total_commits(
    client, 
    config["org_name"], 
    period=(config["start_date"], 
    config["end_date"]))
commit_stats

# %%
commit_stats_filtered = github_utils.get_total_commits(
    client, 
    config["org_name"], 
    period=(config["start_date"], config["end_date"]),
    # Replace with actual GitHub usernames.
    usernames=["heanhsok"]  
)
commit_stats_filtered

# %% [markdown]
# ## Fetch Pull Request Statistics
#
# The `get_total_prs` function retrieves the number of pull requests (PRs) made within the repositories of a specified GitHub organization. This function allows filtering PRs by state, author, and time period.
#
# ### **Parameters**
# - `client` (*Github*): The authenticated GitHub API client.
# - `org_name` (*str*): The name of the GitHub organization.
# - `usernames` (*Optional[List[str]]*): A list of GitHub usernames to filter PRs. If `None`, fetches PRs from all users.
# - `period` (*Optional[Tuple[datetime, datetime]]*): A tuple containing `start_date` and `end_date` to filter PRs within a time range.
# - `state` (*str*, default=`'open'`): The state of the pull requests to fetch. Can be:
#   - `'open'`: Fetch only open PRs.
#   - `'closed'`: Fetch only closed PRs.
#   - `'all'`: Fetch all PRs.

# %%
pr_stats = github_utils.get_total_prs(
    client, 
    config["org_name"], 
    period=(config["start_date"], config["end_date"])
)
pr_stats

# %% [markdown]
# ### Fetching Only Closed PRs

# %%
pr_stats_closed = github_utils.get_total_prs(
    client, 
    config["org_name"], 
    period=(config["start_date"], config["end_date"]),
    state="closed"
)
pr_stats_closed

# %% [markdown]
# ## Fetch Unmerged Pull Request Statistics
#
# The `get_prs_not_merged` function retrieves the count of **closed but unmerged** pull requests (PRs) within the repositories of a specified GitHub organization. This helps identify PRs that were closed without being merged, which could indicate rejected changes or abandoned contributions.
#
# ### **Parameters**
# - `client` (*Github*): The authenticated GitHub API client.
# - `org_name` (*str*): The name of the GitHub organization.
# - `github_names` (*Optional[List[str]]*): A list of GitHub usernames to filter PRs. If `None`, fetches PRs from all users.
# - `period` (*Optional[Tuple[datetime, datetime]]*): A tuple containing `start_date` and `end_date` to filter PRs within a time range.

# %%
unmerged_prs = github_utils.get_prs_not_merged(
    client, 
    config["org_name"], 
    period=(config["start_date"], config["end_date"])
)
unmerged_prs

# %% [markdown]
# ## Fetch Total Issues Statistics
#
# The `get_total_issues` function retrieves the count of issues (excluding pull requests) across all repositories in a GitHub organization. You can filter by issue state (open, closed, or all), a specific time window, or a set of repositories.
#
# ### **Parameters**
# - `client` (*Github*): The authenticated GitHub API client.
# - `org_name` (*str*): The name of the GitHub organization.
# - `repo_names` (*Optional[List[str]]*): List of repository names to search in. If `None`, it fetches from all repositories.
# - `state` (*str*): Can be `"open"`, `"closed"`, or `"all"`. Default is `"open"`.
# - `period` (*Optional[Tuple[datetime, datetime]]*): Tuple containing `start_date` and `end_date` for time filtering.

# %%
# Fetch total issues for the organization
total_issues = github_utils.get_total_issues(
    client,
    config["org_name"],
    state="open",
    period=(config["start_date"], config["end_date"]),
)
total_issues

# %% [markdown]
# ## Fetch Issues Without Assignee
#
# The `get_issues_without_assignee` function returns the number of issues that are **unassigned** across one or more repositories in the organization, within a specified state and time period.
#
# ### **Parameters**
# - `client` (*Github*): The authenticated GitHub API client.
# - `org_name` (*str*): GitHub organization name.
# - `repo_names` (*Optional[List[str]]*): Repositories to include. If `None`, checks all.
# - `state` (*str*): State of issues to consider — `"open"`, `"closed"`, or `"all"`.
# - `period` (*Optional[Tuple[datetime, datetime]]*): Start and end dates for filtering.

# %%
# Fetch issues without assignees
issues_no_assignee = github_utils.get_issues_without_assignee(
    client,
    config["org_name"],
    state="open",
    period=(config["start_date"], config["end_date"]),
)
issues_no_assignee

# %% [markdown]
# ## Fetch Commits by a Specific User
#
# The `get_commits_by_person` function retrieves the number of commits made by a specific GitHub user across repositories in the given organization. This is helpful for assessing an individual’s contribution during a particular time window.
#
# ### **Parameters:**
# - `client` (*Github*): The authenticated GitHub API client.
# - `username` (*str*): GitHub username to filter commits.
# - `org_name` (*str*): GitHub organization name.
# - `period` (*Optional[Tuple[datetime, datetime]]*): Date range to filter commits.

# %%
commit_stats_user = github_utils.get_commits_by_person(
    client,
    # Replace with GitHub username.
    username="heanhsok",  
    org_name=config["org_name"],
    period=(config["start_date"], config["end_date"])
)
commit_stats_user

# %% [markdown]
# ## Fetch Pull Requests by a Specific User
#
# The `get_prs_by_person` function returns the number of pull requests created by a specific GitHub user across all repositories in an organization. This is useful to evaluate code contributions in the form of PRs, optionally filtered by state.
#
# ### **Parameters:**
# - `client` (*Github*): The authenticated GitHub API client.
# - `username` (*str*): GitHub username to filter pull requests.
# - `org_name` (*str*): GitHub organization name.
# - `period` (*Optional[Tuple[datetime, datetime]]*): Date range to filter PRs.
# - `state` (*str*): State of PRs to consider (`'open'`, `'closed'`, or `'all'`).

# %%
prs_stats_user = github_utils.get_prs_by_person(
    client,
    # Replace with GitHub username.
    username="heanhsok",  
    org_name=config["org_name"],
    period=(config["start_date"], config["end_date"]),
    # You can use "open", "closed", or "all".
    state="open"  
)
prs_stats_user

# %% [markdown]
# ## Fetch Unmerged Pull Requests by a Specific User
#
# The `get_prs_not_merged_by_person` function fetches all PRs that were closed but not merged, submitted by a particular GitHub user. This helps identify stale or rejected contributions.
#
# ### **Parameters:**
# - `client` (*Github*): The authenticated GitHub API client.
# - `username` (*str*): GitHub username to filter unmerged PRs.
# - `org_name` (*str*): GitHub organization name.
# - `period` (*Optional[Tuple[datetime, datetime]]*): Date range to filter PRs.

# %%
unmerged_prs_user = github_utils.get_prs_not_merged_by_person(
    client,
    # Replace with GitHub username.
    username="heanhsok",  
    org_name=config["org_name"],
    period=(config["start_date"], config["end_date"])
)
unmerged_prs_user
