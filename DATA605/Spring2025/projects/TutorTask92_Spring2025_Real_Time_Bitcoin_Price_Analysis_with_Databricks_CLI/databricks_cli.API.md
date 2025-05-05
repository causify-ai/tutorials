# Databricks CLI API Documentation

## Project Files

- **`databricks_cli_utils.py`**  
  Core library of all wrapper functions around the Databricks CLI, data fetching, modeling, and plotting.

- **`databricks_cli.API.py`**  
  **Your canonical CLI-demo script.** Run this to exercise every helper in a single, repeatable batch.

- **`databricks_cli.API.ipynb`**  
  Interactive notebook that also imports from `databricks_cli_utils.py`—great for step-by-step exploration, but not needed for automated runs.

- **`config/cluster_config.json`**  
  Sample JSON for creating clusters via CLI.

- **`config/cluster_id.txt`**  
  File where cluster IDs are saved.

---

## 1. Introduction

The Databricks Command Line Interface (CLI) provides a programmatic way to manage Databricks workspaces—clusters, file operations, jobs, runs—without using the web UI.  
This document covers:

1. Setting up the CLI  
2. The key commands used in our Bitcoin-analysis project  
3. How to call them from Python via `databricks_cli_utils.py`  
4. A step-by-step demo in `databricks_cli.API.py` and its companion notebook  

---

## 2. Prerequisites & Setup

### 2.1 Install the Databricks CLI

```bash
pip install databricks-cli
databricks --version
```

### 2.2 Authenticate

Generate a Personal Access Token (PAT) in your Databricks UI:

1. **User Settings → Access Tokens → Generate New Token**  
2. Copy the token immediately.

Configure via terminal:

```bash
databricks configure --token
# When prompted, enter:
#   Databricks Host:   https://<your-workspace>.cloud.databricks.com
#   Token:             <your-PAT>
```

Alternatively, set environment variables:

```bash
export DATABRICKS_HOST=https://<your-workspace>.cloud.databricks.com
export DATABRICKS_TOKEN=<your-PAT>
```

---

## 3. Cluster Configuration

Place your cluster settings in `config/cluster_config.json`.  
Example:

```json
{
  "cluster_name": "bitcoin-analysis-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "num_workers": 1,
  "autotermination_minutes": 60,
  "spark_conf": {
    "spark.databricks.cluster.profile": "singleNode"
  },
  "custom_tags": {
    "Project": "BitcoinAnalysis"
  }
}
```

---

## 4. Core Databricks CLI Commands

### 4.1 Clusters

```bash
databricks clusters create     --json-file config/cluster_config.json
databricks clusters get        --cluster-id <cluster_id>
databricks clusters list
databricks clusters delete     --cluster-id <cluster_id>
```

### 4.2 File System (DBFS)

```bash
databricks fs cp <local> <dbfs:/path>     # upload
databricks fs cp <dbfs:/path> <local>     # download
databricks fs ls <dbfs:/path>
databricks fs mkdirs <dbfs:/path>
databricks fs rm <dbfs:/path>
```

### 4.3 Jobs & Runs

```bash
databricks jobs create       --json-file config/job_config.json
databricks jobs run-now      --job-id <job_id>
databricks runs submit       --json '{...}' 
databricks runs get          --run-id <run_id>
```

---

## 5. Python Wrappers (`databricks_cli_utils.py`)

Each function uses `subprocess` under the hood and returns structured results:

- **`_run_databricks_cli(cmd_list: List[str]) → dict`**  
  Executes a CLI command and captures JSON or raw output.

- **`create_cluster_cli(config_file, cluster_id_file) → str`**  
  Creates a cluster, writes its ID to `cluster_id_file`, and returns it.

- **`get_cluster_status_cli(cluster_id: str) → str`**  
  Returns the cluster’s current state (e.g. `RUNNING`, `TERMINATED`).

- **`upload_to_dbfs_cli(local_path, dbfs_path, overwrite=True) → bool`**  
  Uploads a file to DBFS, optionally overwriting.

- **`download_from_dbfs_cli(dbfs_path, local_path, overwrite=True) → bool`**  
  Downloads a DBFS file locally.

- **`submit_notebook_job_cli(job_id: str) → str`**  
  Triggers a notebook job run and returns its run ID.

- **`get_job_run_status_cli(run_id: str) → dict`**  
  Retrieves job-run status details.

- **`delete_cluster_cli(cluster_id: str) → bool`**  
  Deletes the named cluster (or warns if already gone).

---

## 6. Demo Script: `databricks_cli.API.py`

**Why this matters**  
The `.py` script is the _official_ way to run your API demo end-to-end—ideal for CI, automated testing, or simply “one command and done.”  

The notebook is useful for interactive learning, but if you want deterministic, repeatable runs (e.g. in a shell script or scheduler), you’ll always call:

```bash
python databricks_cli.API.py
```

It will:
1. Create a cluster  
2. Check its status  
3. Upload/download a test file  
4. Submit and poll a job run  
5. Delete the cluster  

All using the same functions that the notebook walks through. 

For line-by-line interactive exploration, open `databricks_cli.API.ipynb`.

---

## 7. References

- **Databricks CLI Documentation**  
  https://docs.databricks.com/dev-tools/cli/index.html

- **Databricks REST API**  
  https://docs.databricks.com/dev-tools/api/latest/

- **Interactive Demo Notebook**  
  `databricks_cli.API.ipynb`

