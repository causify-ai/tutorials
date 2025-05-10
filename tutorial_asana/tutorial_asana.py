# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Asana API Tutorial Notebook
#
# **What this Notebook Does:**
# - Shows how to authenticate and interact with Asana via our custom API layer.
# - Demonstrates how to fetch tasks and comments for a specified project and time period.
# - Computes simple statistics (e.g., tasks created, tasks completed, number of comments).
# - Includes unit tests to ensure the code runs correctly.
#
# **Prerequisites:**
# - A valid Asana Personal Access Token (PAT).
#
# **Instructions:**
# 1. Recommended to your `ASANA_ACCESS_TOKEN` environment variable before running.
#
#
#

# %%
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# %%
import datetime
import logging

import helpers.hdbg as hdbg
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import utils

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

hprint.config_notebook()

# %% [markdown]
# ## Define Config
#
# Here we define all parameters in a single `config` dictionary.
# ou can easily modify:
# - The `project_id` to analyze a different project.
# - The `start_date` and `end_date` to change the timeframe.

# %%
today = datetime.datetime.now()
one_month_ago = today - datetime.timedelta(days=30)
config = {
    # Replace with a valid project ID from your Asana workspace.
    "project_id": ["1208279350109582"],
    "start_date": one_month_ago.isoformat(),
    "end_date": today.isoformat(),
    "access_token": "2/1208871906331279/1208966663406154:1c6f6b89083e73c22241670b11bf00ba",
}

# %% [markdown]
# ## Intialize asana client

# %%
client = utils.AsanaClient(access_token=config["access_token"])
# %% [markdown]
# ## Fetching Task Data
#
#  Using the parameters in `config`, we’ll fetch:
#  - Tasks created within the `start_date` and `end_date`
#  - Tasks completed within the same range
#
#  The `fetch_tasks()` function returns a DataFrame with columns like:
#  - `task_id`
#  - `name`
#  - `assignee`
#  - `created_at`
#  - `completed_at`
#
# %%
# Fetch tasks created in the given period.
tasks_df = utils.fetch_tasks(
    client,
    project_ids=config["project_id"],
    start_date=config["start_date"],
    end_date=config["end_date"],
)
# Fetch tasks completed in the given period.
_LOG.info(
    "Created_taaks_df = \n%s", hpandas.df_to_str(tasks_df, log_level=logging.INFO)
)

# %% [markdown]
# ## Fetching Comments (Stories)
# We now fetch comments for the tasks that were created or completed in the time window.
# `get_task_comments`:
# - Takes a list of task_ids.
# - Returns a DataFrame with `task_id`, `comment_text`, `comment_author`, `comment_created_at`.
#

# %%
task_ids = (
    tasks_df["task_id"].tolist() if not tasks_df.empty else []
)
tasks_comments_df = utils.fetch_comments(client, task_ids)
_LOG.info(
    "Comments df = \n %s",
    hpandas.df_to_str(tasks_comments_df, log_level=logging.INFO),
)

# %% [markdown] magic_args="[markdown]"
# ## Computing Statistics
# We'll compute:
# - Number of tasks created in the period.
# - Number of comments on tasks created in the period.

# %%
num_created_tasks = len(tasks_df)
num_comments_on_created = len(tasks_comments_df)
_LOG.info("Number of tasks created in the period: %s", num_created_tasks)
_LOG.info("Number of comments on created tasks: %s", num_comments_on_created)

# %% [markdown]
# ## Statistics for All Users
#
# We can aggregate by user (assignee) to see how many tasks each user created or completed.
#
# **Tasks Created per User**:
# If `created_tasks_df` includes `assignee`, we can group by that column.
#

# %%
if not tasks_df.empty and "assignee" in tasks_df.columns:
    tasks_created_by_user = (
        tasks_df.groupby("assignee")["task_id"].count().reset_index()
    )
    tasks_created_by_user.columns = ["assignee", "tasks_created_count"]
    print("Tasks Created by User:")
    print(tasks_created_by_user)
else:
    print("No tasks created or 'assignee' information not available.")

# %% [markdown]
# **Tasks Completed per User**:
#
# Similarly, for completed tasks:

# %%
completed_tasks_df = tasks_df[tasks_df["task_status"] == "Completed"]
if not completed_tasks_df.empty and "assignee" in completed_tasks_df.columns:
    tasks_completed_by_user = (
        completed_tasks_df.groupby("assignee")["task_id"].count().reset_index()
    )
    tasks_completed_by_user.columns = ["assignee", "tasks_completed_count"]
    print("Tasks Completed by User:")
    print(tasks_completed_by_user)
else:
    print("No tasks completed or 'assignee' information not available.")

# %% [markdown]
# **Comments per User**:
#
# For comments, we have `author`. We can see how many comments each user made during this period for both created and completed tasks.
#

# %%
if not tasks_comments_df.empty and "author" in tasks_comments_df.columns:
    comments_by_user = (
        tasks_comments_df.groupby("author")["task_id"].count().reset_index()
    )
    comments_by_user.columns = ["author", "comments_count"]
    print("Comments by User:")
    print(comments_by_user)
else:
    print("No comments found or 'comment_author' information not available.")
