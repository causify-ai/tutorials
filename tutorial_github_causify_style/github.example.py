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
# # Assessing Developer Performance via GitHub API
#
# ## Introduction
#
# This notebook demonstrates how to use a custom Python-based wrapper around the GitHub API to **analyze developer activity** and **contributions** within an organization. It provides practical tools for engineering managers, team leads, and data analysts to measure productivity and engagement over time.
#
# GitHub stores a wealth of activity data such as commits, pull requests (PRs), and issue interactions. However, extracting meaningful insights from GitHub’s native API can be challenging due to its raw structure and pagination mechanisms. To simplify this, we’ve built a software layer that exposes **clean**, and **high-level functions** that return structured metrics ready for analysis.
#
# With these APIs, you can:
#
# - Track contributions of individual developers (commits, PRs, unmerged work).
# - Compare productivity across teammates.
# - Identify your most active or consistent contributors.
# - Visualize patterns across repositories and timeframes.
# - Support engineering OKRs, sprint planning, and retrospectives with data.
#
# Throughout this notebook, we’ll implement real-life scenarios that use these APIs and visualize the insights with interactive Plotly charts.

# %% [markdown]
# ## Potential Applications
#
# Our custom GitHub API layer enables a wide range of data-driven assessments of developer activity and repository health. Below are some practical use cases that can be directly implemented using the APIs exposed by our software layer.
#
# ### Individual Developer Contribution Report
# Generate a personal activity summary for a specific contributor within a defined time range. Metrics include:
# - Number of commits across repositories.
# - Number of pull requests (PRs) created.
# - Count of unmerged or closed PRs.
# - Issue involvement and assignments.
#
# > **Use case:** Great for quarterly reviews or self-assessments.
#
# ### Comparative Productivity Analysis
# Compare the contributions of two or more developers using metrics such as:
# - Commits per repository.
# - PRs submitted and merged.
# - Frequency of contributions.
#
# > **Use case:** Helps team leads assess team balance, recognize underappreciated efforts, or allocate resources more efficiently.
#
# ### Identify Most Active Contributors
# Scan an entire organization and rank users based on contribution statistics such as:
# - Total commits.
# - PR activity (opened/merged).
# - Issues closed or managed.
#
# > **Use case:** Identify top performers or potential mentors in the team.
#
# ### Stale or Unmerged PR Monitoring
# Detect PRs that have been closed but not merged. These could indicate:
# - Abandoned or rejected work.
# - PRs needing review attention.
#
# > **Use case:** Improve code review cycles and minimize wasted effort.
#
# ### Open Issues Without Assignees
# Track unassigned issues to ensure tasks are distributed and prioritized appropriately.
#
# > **Use case:** Project managers can use this to ensure no work falls through the cracks.
#
# ### Team-Level Activity Heatmaps
# Generate visual dashboards showing activity across teams or projects:
# - Contribution volume by repository.
# - Commit spikes over time.
#
# > **Use case:** Great for retrospectives, planning meetings, or engineering leadership reports.

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
from github import Github
from datetime import datetime, timedelta
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
# ## Scenario 1: Individual Developer Contribution Report
#
# This section generates a contribution summary for a single developer in the organization across all repositories over a given time window.
#
# We’ll compute:
# - Total commits
# - PRs created
# - Closed but unmerged PRs
# - Commits per repository
# - PRs per repository
#
# These insights can be used in developer 1:1s, performance evaluations, or self-tracking.

# %% vscode={"languageId": "plaintext"}
# Choose developer to analyze.
developer_username = "heanhsok"

# Compute contribution statistics.
commits_by_user = github_utils.get_commits_by_person(
    client, developer_username, config["org_name"],
    period=(config["start_date"], config["end_date"])
)
prs_by_user = github_utils.get_prs_by_person(
    client, developer_username, config["org_name"],
    period=(config["start_date"], config["end_date"]),
    state="all"
)
unmerged_prs_by_user = github_utils.get_prs_not_merged_by_person(
    client, developer_username, config["org_name"],
    period=(config["start_date"], config["end_date"])
)

# Display raw output (optional).
commits_by_user, prs_by_user, unmerged_prs_by_user

# %% [markdown]
# ### Visualization

# %% vscode={"languageId": "plaintext"}
# Convert dictionaries to dataframes for visualization.
df_commits = (
    pd.DataFrame.from_dict(commits_by_user["commits_per_repository"], orient="index", columns=["Commits"])
    .reset_index().rename(columns={"index": "Repository"})
)
df_prs = (
    pd.DataFrame.from_dict(prs_by_user["prs_per_repository"], orient="index", columns=["PRs"])
    .reset_index().rename(columns={"index": "Repository"})
)

# Plotly Bar Charts.
fig_commits = px.bar(
    df_commits, x="Repository", y="Commits",
    title=f"Commits by {developer_username}",
    labels={"Commits": "Number of Commits"}, text="Commits"
)
fig_commits.show()

fig_prs = px.bar(
    df_prs, x="Repository", y="PRs",
    title=f"Pull Requests by {developer_username}",
    labels={"PRs": "Number of PRs"}, text="PRs"
)
fig_prs.show()

# %% [markdown]
# ### Summary
#
# - **Total Commits:** 33
# - **Total PRs:** 39
# - **Unmerged PRs:** 10
#
# This snapshot gives a clear view of how actively the developer has contributed via code commits and PRs. It’s also useful to identify how many PRs were potentially abandoned or rejected.

# %% [markdown]
# ## Scenario 2: Comparative Productivity Analysis Between Two Developers
#
# In this section, we compare two developers based on:
# - Total commits made
# - Number of PRs opened
# - Number of PRs closed but not merged
#
# This type of analysis can be useful in:
# - Sprint retrospectives
# - Internal performance benchmarking
# - Identifying trends or support needs in collaborative teams
#
# We will display these comparisons using interactive Plotly bar charts.
#

# %%
# Define developer GitHub usernames.
usernames = ["heanhsok", "Shaunak01"]

# Initialize results container.
comparison_results = []

# Collect metrics for each user.
for username in usernames:
    commits_data = github_utils.get_commits_by_person(
        client, username, config["org_name"],
        period=(config["start_date"], config["end_date"])
    )
    prs_data = github_utils.get_prs_by_person(
        client, username, config["org_name"],
        period=(config["start_date"], config["end_date"]),
        state="all"
    )
    unmerged_data = github_utils.get_prs_not_merged_by_person(
        client, username, config["org_name"],
        period=(config["start_date"], config["end_date"])
    )
    
    comparison_results.append({
        "Username": username,
        "Commits": commits_data["total_commits"],
        "Total PRs": prs_data["total_prs"],
        "Unmerged PRs": unmerged_data["prs_not_merged"]
    })

# Create DataFrame.
df_comparison = pd.DataFrame(comparison_results)
df_comparison

# %% [markdown]
# ### Visualization

# %%
# Commits Comparison.
fig_commits = px.bar(
    df_comparison, x="Username", y="Commits",
    title="Total Commits per Developer",
    text="Commits", color="Username"
)
fig_commits.show()

# PRs Comparison.
fig_prs = px.bar(
    df_comparison, x="Username", y="Total PRs",
    title="Total PRs per Developer",
    text="Total PRs", color="Username"
)
fig_prs.show()

# Unmerged PRs Comparison.
fig_unmerged_prs = px.bar(
    df_comparison, x="Username", y="Unmerged PRs",
    title="Unmerged PRs per Developer",
    text="Unmerged PRs", color="Username"
)
fig_unmerged_prs.show()

# %% [markdown]
# ### Summary
#
# - The charts above clearly show the level of activity for each developer.
# - Higher PRs but lower commits may indicate feature-focused contributions.
# - A high number of unmerged PRs might indicate the need for support or review process delays.
#
# Use this analysis to support reviews, sprint demos, or identify developer bottlenecks.

# %% [markdown]
# ## Scenario 3: Identify Top Contributors in an Organization
#
# In this section, we use our GitHub API wrapper to identify the top contributors in an organization based on the total number of commits.
#
# This information is useful for:
# - End-of-sprint retrospectives
# - Contribution reports
# - Recognizing high performers
# - Spotting contribution bottlenecks (e.g., frequent unmerged PRs)
#
# We will display the top contributors using interactive bar charts.

# %%
# Get all repositories in the organization.
repo_list = github_utils.get_repo_names(client, config["org_name"])["repositories"]
qualified_repos = [f"{config['org_name']}/{repo}" for repo in repo_list]

# Get contributors across all repos.
contributors_dict = github_utils.get_github_contributors(client, qualified_repos)

# Flatten the list of contributors and remove duplicates.
unique_contributors = list(set(chain.from_iterable(contributors_dict.values())))
print(f" Found {len(unique_contributors)} unique contributors.")

# Gather metrics for each contributor.
top_contributor_stats = []
for user in unique_contributors:
    commit_data = github_utils.get_commits_by_person(client, user, config["org_name"], period=(config["start_date"], config["end_date"]))
    
    top_contributor_stats.append({
        "Username": user,
        "Commits": commit_data["total_commits"],
    })

# Create DataFrame and sort.
df_top_contributors = pd.DataFrame(top_contributor_stats)
df_top_contributors_sorted = df_top_contributors.sort_values(by="Commits", ascending=False).reset_index(drop=True)
df_top_contributors_sorted.head(10)


# %% [markdown]
# ### Visualization

# %%
# Top 10 Contributors by Commits.
fig_top_commits = px.bar(
    df_top_contributors_sorted.head(10),
    x="Username", y="Commits",
    title="Top 10 Contributors by Commits",
    text="Commits", color="Username"
)
fig_top_commits.show()


# %% [markdown]
# ### Summary
#
# - The above charts show the most active contributors for the total number of commits.
# - You can also filter by time to run this analysis per sprint, quarter, or release cycle.

# %% [markdown]
# ## Wrap-up and Insights
#
# In this notebook, we demonstrated how to use our custom GitHub API layer to generate performance analytics for contributors within an organization. These insights can help engineering managers, project leads, and contributors themselves to better understand and improve collaboration on GitHub.
#
# ### Key Takeaways
#
# - **Individual-level Tracking**: Using `get_commits_by_person`, `get_prs_by_person`, and related functions, you can track the contributions of specific users across time.
# - **Comparative Analysis**: With visualizations, it becomes easier to compare contributions between developers and uncover collaboration patterns.
# - **Identifying Stale Work**: Unmerged PR analysis helps flag efforts that didn’t result in merged changes—providing opportunities to investigate blockers or improve review processes.
# - **Top Contributor Reporting**: You can rank contributors and recognize their efforts across repositories, which is useful for performance reviews, public recognition, or retrospectives.
#
# ### How to Use These Insights
#
# - **Team Leads** can use this data in sprint reviews, retrospectives, and quarterly evaluations.
# - **Data Analysts** can plug this data into dashboards to measure long-term contribution trends.
# - **HR/Leadership** can identify top performers for recognition or incentives.
# - **Developers** themselves can use the analytics to spot unmerged work or improve PR hygiene.
#
# ### What's Next?
#
# This tutorial can serve as a foundation for:
#
# - Automated dashboards (e.g., using Streamlit or Dash)
# - Contributor heatmaps
# - ML-based anomaly detection in contributor patterns
# - Integration with GitHub Actions for real-time reporting
#
# Feel free to extend the APIs or visualizations further based on your team's specific KPIs or workflow needs.
