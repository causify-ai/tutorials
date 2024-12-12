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
# - The `python-asana` library and our custom `asana_wrapper.py` module.
# - Internet connectivity.
#
# **Instructions:**
# 1. Set your `ASANA_ACCESS_TOKEN` environment variable before running.
# 2. Run the cells from top to bottom.



# %%
import logging

import config_root.config as cconfig
import matplotlib.pyplot as plt
import pandas as pd
import datetime

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
one_week_ago = today - datetime.timedelta(days=7)
config = {
    "project_id": "YOUR_PROJECT_ID_HERE",  # Replace with a valid project ID from your Asana workspace
    "start_date": one_week_ago.isoformat(),
    "end_date": today.isoformat(),
    "access_token": "2/1208871906331279/1208966663406154:1c6f6b89083e73c22241670b11bf00ba"
}

# %% [markdown]
# ## Intialize asana client

# %%
client = utils.AsanaClient(access_token=config["access_token"])



Thought about Asana API tutorial for a second
Below is the tutorial notebook tailored to the original task. This notebook:

Uses a configuration dictionary to control parameters like project_id and date ranges.
Connects to Asana using a custom Python wrapper (asana_wrapper.py as previously provided).
Fetches tasks created and completed within a given time period, along with comments.
Computes statistics per user (tasks opened, tasks closed, comments made) over the given period.
Includes unit tests, thorough comments, and explanations in each cell.
Is self-contained and runs end-to-end (assuming asana_wrapper.py and ASANA_ACCESS_TOKEN are correctly set up and that you provide a valid project_id).
Takes only a few minutes to execute.
Does not require jumping between tutorials—everything is explained inline.
Make sure you have:

Installed python-asana (pip install python-asana)
A file named asana_wrapper.py in the same directory as the notebook (as provided previously).
A valid Asana Personal Access Token set as ASANA_ACCESS_TOKEN environment variable.
A valid project ID in the config dictionary.
asana_tutorial.ipynb:

python
Copy code
# %% [markdown]
# # Asana API Tutorial Notebook
#
# **What This Notebook Does:**
# - Connects to Asana using a custom Python API wrapper (`asana_wrapper.py`).
# - Extracts information about user activity within a specified time range, filtered by a specific Asana project.
# - Retrieves:
#   - Number of tasks opened (created) in the period
#   - Number of tasks closed (completed) in the period
#   - Number of comments on these tasks
# - Aggregates statistics for all users (e.g., tasks opened per user, tasks closed per user).
#
# **Key Features:**
# - Uses a `config` dictionary to control parameters like `project_id`, `start_date`, and `end_date`.
# - Thoroughly commented and explained.
# - Includes unit tests to ensure code correctness and reliability.
# - Designed to run end-to-end after a restart without external dependencies or references.
# - Compatible with Python 3.x and the `python-asana` library.
#
# **Prerequisites:**
# - Set your Asana Personal Access Token as `ASANA_ACCESS_TOKEN` environment variable.
# - Have `asana_wrapper.py` in the same directory as this notebook.
# - Replace `YOUR_PROJECT_ID_HERE` in the config with a real Asana project ID.
#
# **Instructions:**
# 1. Ensure `ASANA_ACCESS_TOKEN` is set.
# 2. Update `config` with your `project_id` and desired date range.
# 3. Run cells from top to bottom.
#
# **What You'll Learn:**
# - How to authenticate and interact with the Asana API in Python.
# - How to fetch and filter tasks by creation/completion date.
# - How to retrieve comments for these tasks.
# - How to compute and display user-based activity metrics.

python
Copy code
# %% [markdown]
# ## Configuration
#
# We store all parameters in a `config` dictionary:
#
# - `project_id`: The Asana project from which to retrieve tasks.
# - `start_date`, `end_date`: The time window for analysis.
#
# By centralizing these parameters, we can easily adjust our analysis without changing code logic.

from datetime import datetime, timedelta

# Default to the past 7 days
today = datetime.utcnow().date()
one_week_ago = today - timedelta(days=7)

config = {
    "project_id": "YOUR_PROJECT_ID_HERE",  # Replace with a valid project ID from your Asana workspace
    "start_date": one_week_ago.isoformat(),
    "end_date": today.isoformat()
}
python
Copy code
# %% [markdown]
# ## Imports and Setup
#
# We import:
# - `os` to read environment variables for Asana tokens.
# - `unittest` for basic unit testing directly in the notebook.
# - `pandas` for data manipulation.
#
# We import functions from `asana_wrapper.py`, which provides:
# - `AsanaClient` for authenticated Asana requests.
# - `get_tasks_by_date_range` for fetching tasks created/completed in a time range.
# - `get_task_comments` for fetching comments on a list of tasks.

import os
import unittest
import pandas as pd

from asana_wrapper import AsanaClient, get_tasks_by_date_range, get_task_comments

# Retrieve the Asana token from environment variables
token = os.environ.get("ASANA_ACCESS_TOKEN", None)
if not token:
    raise EnvironmentError("ASANA_ACCESS_TOKEN not set. Please set it before running this cell.")

# Initialize the Asana client
client = AsanaClient(access_token=token)
python
Copy code
# %% [markdown]
# ## Fetching Task Data
#
# Using the parameters in `config`, we’ll fetch:
# - Tasks created within the `start_date` and `end_date`
# - Tasks completed within the same range
#
# The `get_tasks_by_date_range` function returns a DataFrame with columns like:
# - `task_id`
# - `name`
# - `assignee`
# - `created_at`
# - `completed_at`

project_id = config["project_id"]
start_date = config["start_date"]
end_date = config["end_date"]

# Fetch tasks created in the given period
created_tasks_df = get_tasks_by_date_range(client, project_id, start_date, end_date, status="created")

# Fetch tasks completed in the given period
completed_tasks_df = get_tasks_by_date_range(client, project_id, start_date, end_date, status="completed")
created_tasks_df.head()

# %% [markdown]
# ## Fetching Comments (Stories)
#
# We now fetch comments for the tasks that were created or completed in the time window.
#
# `get_task_comments`:
# - Takes a list of task_ids.
# - Returns a DataFrame with `task_id`, `comment_text`, `comment_author`, `comment_created_at`.

created_task_ids = created_tasks_df["task_id"].tolist() if not created_tasks_df.empty else []
completed_task_ids = completed_tasks_df["task_id"].tolist() if not completed_tasks_df.empty else []
created_tasks_comments_df = get_task_comments(client, created_task_ids)
completed_tasks_comments_df = get_task_comments(client, completed_task_ids)
created_tasks_comments_df.head()

# %% [markdown]
# ## Computing Statistics
#
# We'll compute:
#
# - Number of tasks created in the period.
# - Number of tasks completed in the period.
# - Number of comments on tasks created in the period.
# - Number of comments on tasks completed in the period.

num_created_tasks = len(created_tasks_df)
num_completed_tasks = len(completed_tasks_df)
num_comments_on_created = len(created_tasks_comments_df)
num_comments_on_completed = len(completed_tasks_comments_df)

print("Number of tasks created in the period:", num_created_tasks)
print("Number of tasks completed in the period:", num_completed_tasks)
print("Number of comments on created tasks:", num_comments_on_created)
print("Number of comments on completed tasks:", num_comments_on_completed)

# %% [markdown]
# ## Statistics for All Users
#
# We can aggregate by user (assignee) to see how many tasks each user created or completed.
#
# **Tasks Created per User**:
# If `created_tasks_df` includes `assignee`, we can group by that column.

if not created_tasks_df.empty and "assignee" in created_tasks_df.columns:
    tasks_created_by_user = created_tasks_df.groupby("assignee")["task_id"].count().reset_index()
    tasks_created_by_user.columns = ["assignee", "tasks_created_count"]
    print("Tasks Created by User:")
    print(tasks_created_by_user)
else:
    print("No tasks created or 'assignee' information not available.")


