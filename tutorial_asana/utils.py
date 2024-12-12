import logging
from typing import Any, List, Callable

import asana
import pandas as pd
from datetime import datetime
import time
import helpers.hdbg as hdbg


_LOG = logging.getLogger(__name__)

class AsanaClient:
    def __init__(self, access_token: str) -> None:
        """
        Initialize the Asana client using a personal access token.

        :param access_token: a valid Asana personal access token
        """
        configuration = asana.Configuration()
        configuration.access_token = access_token
        self.api_client = asana.ApiClient(configuration)
        self.tasks_api = asana.TasksApi(self.api_client)
        self.comments_api = asana.StoriesApi(self.api_client)


def fetch_with_retries(
    func: Callable[..., Any],  
    *args: Any, 
    retries: int = 3,  
    delay: int = 2,  
    **kwargs: Any  
) -> Any:
    """
    Helper function to retry API calls in case of transient errors.

    :param func: function to be called
    :param args: positional arguments for the function
    :param retries: number of retries
    :param delay: delay between retries in seconds
    :param kwargs: keyword arguments for the function
    :return: result of the function call
    """
    # 
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except asana.rest.ApiException as e:
            if e.status == 429:  # Rate limit exceeded
                retry_after = int(e.body.get("retry_after", delay)) if e.body else delay
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            elif e.status >= 500:  # Server error
                print(f"Server error encountered: {e.reason}. Retrying...")
                time.sleep(delay)
            else:
                # Raise for non-retriable errors
                print(f"API Error (Status: {e.status}): {e.reason}")
                print(f"Details: {e.body}")
                raise e
    raise Exception(f"Max retries reached for {func.__name__}")


def fetch_tasks(
    client: AsanaClient, 
    project_ids: List[str], 
    start_date: str, 
    end_date: str
) -> pd.DataFrame:
    """
    Fetch tasks from multiple projects and filter by date range.

    :param client: AsanaClient instance
    :param project_ids: list of project IDs
    :param start_date: start date in the format "YYYY-MM-DD"
    :param end_date: end date in the format "YYYY-MM-DD"
    :return: consolidated DataFrame
    """
    
    all_tasks = []
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    # Iterate over project IDs.
    for project_id in project_ids:
        try:
            # Fetch tasks for each project.
            tasks = fetch_with_retries(
                client.tasks_api.get_tasks_for_project,
                {"project": project_id, "opt_fields": "name,assignee.name,completed_at,created_at"}
            )
            df = pd.DataFrame(tasks["data"])
            if not df.empty:
                # Rename and parse fields.
                df.rename(columns={"gid": "task_id"}, inplace=True)
                df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
                df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
                df["assignee"] = df["assignee"].apply(lambda x: x["name"] if isinstance(x, dict) else None)
                # Add project ID for context.
                df["project_id"] = project_id  
                # Filter by date range.
                df = df[
                    (df["created_at"] >= start_dt) &
                    (df["created_at"] < end_dt)
                ]
                # Append to the consolidated DataFrame.
                all_tasks.append(df)
        # Handle if API call fails.
        except asana.rest.ApiException as e:
            _LOG.debug(f"Failed to fetch tasks for project {project_id}: {e.reason} (Status: {e.status})")
            _LOG.debug(f"Details: {e.body}")
    # Concatenate all tasks into a single DataFrame.
    if all_tasks is not None:
        df = pd.concat(all_tasks, ignore_index=True)
    else:
        # Return an empty DataFrame if no tasks are found.
        df = pd.DataFrame(columns=["task_id", "name", "assignee", "created_at", "completed_at", "project_id"])
    return df


def fetch_comments(client: AsanaClient, task_id: str) -> pd.DataFrame:
    """
    Fetch comments for a given task.

    :param client: AsanaClient instance
    :param task_id: ID of the task to fetch comments for
    :return: df of comments
    """
    # Fetch comments.
    try:
        # Fetch comments (stories) for the task.
        stories = fetch_with_retries(
            client.comments_api.get_stories_for_task,
            task_id,
            {"opt_fields": "text,created_at,created_by.name,resource_subtype"}
        )
        comments = [
            {
                "task_id": task_id,
                "text": s.get("text", ""),
                "author": s.get("created_by", {}).get("name", None),
                "created_at": s.get("created_at")
            }
            for s in stories if s.get("resource_subtype") == "comment_added"
        ]
        df =  pd.DataFrame(comments)
    # Handle if API call fails.
    except asana.rest.ApiException as e:
        _LOG.debug(f"Failed to fetch comments for task {task_id}: {e.reason} (Status: {e.status})", only_warning=True)
        _LOG.debug(f"Details: {e.body}", only_warning=True)
        df = pd.DataFrame(columns=["task_id", "text", "author", "created_at"])
    # Return the DataFrame.
    return df

def get_user_activity_stats(tasks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute statistics for all users from tasks.

    :param tasks_df: df of tasks
    :return: df with user activity statistics
    """
    # Group by assignee and count tasks opened and closed.
    return tasks_df.groupby("assignee").agg(
        tasks_opened=("task_id", "count"),
        tasks_closed=("completed_at", lambda x: x.notnull().sum())
    ).reset_index()


def get_comments_stats(client: AsanaClient, tasks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute comment statistics for tasks.

    :param client: AsanaClient instance
    :param tasks_df: df of tasks
    :return: df with comment statistics
    """
    all_comments = pd.concat(
        [fetch_comments(client, task_id) for task_id in tasks_df["task_id"]],
        ignore_index=True
    )
    return all_comments.groupby("author").size().reset_index(name="comments_count")


