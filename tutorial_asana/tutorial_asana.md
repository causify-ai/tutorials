# Asana API Wrapper Documentation

This document explains the underlying endpoints used in the `AsanaClient` wrapper, followed by an explanation of the utility functions provided in the [utils.py](tutorials_asana/utils.py) file.

---

## **Endpoints Used in the Wrapper**

### 1. **Tasks API**
   - **Endpoint**: `GET /projects/{project_gid}/tasks`
     - **Usage**: Retrieves tasks for a specific project.
   - **Endpoint**: `GET /tasks/{task_gid}/stories`
     - **Usage**: Fetches stories (comments) for a specific task.

### 2. **Projects API**
   - **Endpoint**: `GET /projects/{project_gid}`
     - **Usage**: Fetches details of a specific project, including its archived status.

### 3. **Stories API**
   - **Endpoint**: `GET /tasks/{task_gid}/stories`
     - **Usage**: Used to fetch comments for a task.

---

## **Functions in the Wrapper**

### 1. **`AsanaClient`**
   This class initializes the Asana client using a personal access token. It sets up the APIs for tasks, projects, and comments to enable easy interaction with Asana's API.

---

### 2. **`fetch_with_retries`**
   A helper function that ensures retry logic for API calls in case of transient errors, such as rate limits (`429`) or server errors (`5xx`). 

   - **How it Works**: 
     - Retries the API call a specified number of times (`retries`).
     - Implements exponential backoff for rate-limiting errors.

---

### 3. **`fetch_tasks`**
   Fetches tasks from multiple projects and filters them by a specified date range. It adds metadata such as project status (Active/Completed) and task status (Completed/Incomplete).

   - **Key Features**:
     - Retrieves tasks from the `GET /projects/{project_gid}/tasks` endpoint.
     - Adds project-level metadata like `project_status` and task-level metadata like `task_status`.
     - Filters tasks based on the `created_at` date range.

---

### 4. **`fetch_comments`**
   Fetches all comments (stories) for a list of tasks.

   - **Key Features**:
     - Calls the `GET /tasks/{task_gid}/stories` endpoint to fetch comments.
     - Extracts key information: comment text, author, and creation date.
     - Returns a DataFrame consolidating comments across all tasks.

---

### 5. **`get_user_activity_stats`**
   Computes user activity statistics based on the tasks DataFrame.

   - **Key Features**:
     - Aggregates the number of tasks opened and closed for each user (`assignee`).
     - Helps track user productivity and task closure rates.

---

### 6. **`get_comments_stats`**
   Computes comment statistics for all users based on the comments retrieved for tasks.

   - **Key Features**:
     - Fetches comments using `fetch_comments` for all tasks.
     - Aggregates the number of comments authored by each user.

---

