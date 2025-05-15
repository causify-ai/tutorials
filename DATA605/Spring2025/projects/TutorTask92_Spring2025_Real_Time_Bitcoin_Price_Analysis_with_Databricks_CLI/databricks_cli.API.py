"""
Demonstrates each Databricks‐CLI helper in databricks_cli_utils.py.

Usage:
    python databricks_cli.API.py

Functions:
    create_cluster(): launch a cluster and return its ID
    get_cluster_status(cluster_id): fetch the cluster’s state
    upload_file(local, dbfs): copy a file into DBFS
    download_file(dbfs, local): retrieve a file from DBFS
    submit_notebook(job_id): run a notebook job
    get_run_status(run_id): check job state
    delete_cluster(cluster_id): tear down the cluster

See also: databricks_cli.API.md
"""

from databricks_cli_utils import (
    create_cluster_cli,
    get_cluster_status_cli,
    upload_to_dbfs_cli,
    download_from_dbfs_cli,
    submit_notebook_job_cli,
    get_job_run_status_cli,
    delete_cluster_cli,
)

def create_cluster():
    """Create a cluster via CLI and return its ID."""
    return create_cluster_cli("config/cluster_config.json", "config/cluster_id.txt")

def get_cluster_status(cluster_id: str) -> str:
    """Return the current status of a cluster."""
    return get_cluster_status_cli(cluster_id)

def upload_file(local_path: str, dbfs_path: str) -> bool:
    """Upload a local file to DBFS."""
    return upload_to_dbfs_cli(local_path, dbfs_path)

def download_file(dbfs_path: str, local_path: str) -> bool:
    """Download a file from DBFS to local disk."""
    return download_from_dbfs_cli(dbfs_path, local_path)

def submit_notebook(job_id: str) -> str:
    """Submit a notebook job and return its run ID."""
    return submit_notebook_job_cli(job_id)

def get_run_status(run_id: str) -> dict:
    """Get the state of a submitted run."""
    return get_job_run_status_cli(run_id)

def delete_cluster(cluster_id: str) -> bool:
    """Delete the specified cluster."""
    return delete_cluster_cli(cluster_id)

def main():
    cid = create_cluster()
    print("Cluster created:", cid)

    status = get_cluster_status(cid)
    print("Cluster status:", status)

    ok = upload_file("data/bitcoin_price.json", "dbfs:/tmp/bitcoin.json")
    print("Uploaded?", ok)

    ok = download_file("dbfs:/tmp/bitcoin.json", "data/downloaded.json")
    print("Downloaded?", ok)

    run_id = submit_notebook("12345")
    print("Run ID:", run_id)

    run_state = get_run_status(run_id)
    print("Run status:", run_state)

    deleted = delete_cluster(cid)
    print("Deleted?", deleted)

if __name__ == "__main__":
    main()
