#!/usr/bin/env python3
"""
Download metadata from the EIA v2 API and upload it to S3.

Usage:
> python download_eia_metadata.py --category <CATEGORY> --api_key <API_KEY> --version_num <VERSION_NUM>

This script traverses the EIA v2 API under a specified category, collects all time series 
metadata, and writes the metadata and associated parameter values to an S3 bucket in versioned
CSV files.

Outputs:
    - A flattened metadata index (one row per frequency and metric combination).
    - A parameter (facet value) CSV per dataset.

Arguments:
    --category       Root category path under the EIA v2 API.
    --api_key        EIA API key used to authenticate requests.
    --version_num    Metadata version used in filenames and output paths (e.g., '1.0').
"""

import argparse
import csv
import io
import os
import logging
from typing import Any, Dict, List

import helpers.hdbg as hdbg
import helpers.hparser as hparser
import helpers.hs3 as hs3
import pandas as pd
import requests

_LOG = logging.getLogger(__name__)

BASE_URL = "https://api.eia.gov/v2"

# #############################################################################
# API interaction
# #############################################################################


def _get_api_request(route: str, api_key: str) -> Dict[str, Any]:
    """
    Retrieve JSON data from a given EIA v2 API route.

    This function sends a GET request to the specified EIA v2 API endpoint
    and returns the parsed content from the "response" key.

    Example output:
    {
        "id": "retail-sales",
        "name": "Electricity Sales to Ultimate Customers",
        "description": "Electricity sales to ultimate customer by state and sector. 
            Sources: Forms EIA-826, EIA-861, EIA-861M",
        "frequency": [
            {"id": "monthly", "format": "YYYY-MM"},
            ...
        ],
        "facets": [
            {"id": "stateid", "description": "State / Census Region"},
            ...
        ],
        "data": {
            "revenue": {
                "alias": "Revenue from Sales to Ultimate Customers",
                "units": "million dollars"
            },
            ...
        },
        "startPeriod": "2001-01",
        "endPeriod": "2025-01",
        "defaultDateFormat": "YYYY-MM",
        "defaultFrequency": "monthly"
    }

    :param route: endpoint path like "electricity/retail-sales"
    :param api_key: EIA API key
    :return: content from the EIA API response
    """
    # Build the full API request URL.
    url = f"{BASE_URL}/{route}?api_key={api_key}"
    # Send HTTP GET request to the EIA API.
    response = requests.get(url, timeout=20)
    # Parse JSON content.
    json_data = response.json()
    # Get response from parsed payload.
    data: Dict[str, Any] = {}
    data = json_data.get("response", {})
    return data


def _extract_metadata(
    data: Dict[str, Any], route: str, version_num: str
) -> List[Dict[str, Any]]:
    """
    Extract and flatten relevant metadata fields from a single API response.

    For each frequency and metric combination in the dataset, construct a flat
    metadata record containing API query details, dataset properties, frequency
    info, metric info, and associated file paths.

    Example output:
    [
        {
            "url": "https://api.eia.gov/v2/electricity/retail-sales?api_key={API_KEY}&frequency=monthly&data[0]=revenue",
            "id": "retail_sales_monthly_revenue",
            "dataset_id": "retail_sales",
            "name": "Electricity Sales to Ultimate Customers",
            "description": "...",
            "frequency_id": "monthly",
            "frequency_alias": ...,
            "frequency_description": "One data point for each month.",
            "frequency_query": "M",
            "frequency_format": "YYYY-MM",
            "facets": [
                {"id": "stateid", "description": "State / Census Region"},
                {"id": "sectorid", "description": "Sector"}
            ],
            "data": "revenue",
            "data_alias": "Revenue from Sales to Ultimate Customers",
            "data_units": "million dollars",
            "start_period": "2001-01",
            "end_period": "2025-01",
            "parameter_values_file": "eia_parameters_v1.0/retail_sales_parameters.csv"
        },
        ...
    ]

    :param data: API response content for a leaf endpoint
    :param route: full route path used to access this response
    :param version_num: version number of output paths
    :return: flattened metadata fields
    """
    frequencies = data.get("frequency")
    metrics = data.get("data")
    flattened_metadata = []
    for frequency in frequencies:
        for metric_id, metric_info in metrics.items():
            # Clean up IDs for use in CSVs or DBs.
            frequency_id = frequency.get("id")
            dataset_id = data.get("id")
            dataset_id_clean = dataset_id.replace("-", "_")
            metric_id_clean = metric_id.replace("-", "_")
            # Construct a placeholder API URL.
            url = (
                f"{BASE_URL}/{route}"
                f"?api_key={{API_KEY}}"
                f"&frequency={frequency_id}"
                f"&data[0]={metric_id}"
            )
            # Determine parameter CSV path for associated facet values.
            param_file_path = (
                f"eia_parameters_v{version_num}/{dataset_id_clean}_parameters.csv"
            )
            # Flattened metadata row for one frequency and metric combination.
            metadata = {
                "url": url,
                "id": f"{dataset_id_clean}_{frequency_id}_{metric_id_clean}",
                "dataset_id": dataset_id_clean,
                "name": data.get("name"),
                "description": data.get("description"),
                "frequency_id": frequency.get("id"),
                "frequency_alias": frequency.get("alias"),
                "frequency_description": frequency.get("description"),
                "frequency_query": frequency.get("query"),
                "frequency_format": frequency.get("format"),
                "facets": data.get("facets"),
                "data": metric_id,
                "data_alias": metric_info.get("alias"),
                "data_units": metric_info.get("units"),
                "start_period": data.get("startPeriod"),
                "end_period": data.get("endPeriod"),
                "parameter_values_file": param_file_path,
            }
            flattened_metadata.append(metadata)
    return flattened_metadata


def _get_leaf_route_data(
    root_route: str, api_key: str
) -> Dict[str, Dict[str, Any]]:
    """
    Traverse the API tree and collect metadata from all leaf routes.

    This function performs a breadth-first traversal over all sub-routes beginning at
    `root_route`. For each route that has no children (i.e., a leaf), it fetches and stores
    the associated metadata.

    Example output:
    {
        "electricity/retail-sales": {
            "id": "retail-sales",
            "name": "Electricity Sales to Ultimate Customers",
            "frequency": [...],
            "facets": [...],
            "data": {...},
            "startPeriod": "2001-01",
            "endPeriod": "2025-01",
            "defaultDateFormat": "YYYY-MM",
            "defaultFrequency": "monthly"
        },
        ...
    }

    :param root_route: root category route
    :param api_key: EIA API key
    :return: all leaf routes and their data payloads
    """
    # Create a queue to hold routes to explore.
    queue = [root_route]
    leaf_route_data = {}
    # Traverse and collect all leaf routes.
    while queue:
        current_route = queue.pop(0)
        data = _get_api_request(current_route, api_key)
        if not data:
            continue
        children = data.get("routes", [])
        if children:
            # Add route children to the queue.
            for child in children:
                child_id = child["id"]
                queue.append(f"{current_route}/{child_id}")
        else:
            # Record the leaf route.
            leaf_route_data[current_route] = data
    return leaf_route_data


def _get_facet_values(
    metadata: Dict[str, Any], route: str, api_key: str
) -> pd.DataFrame:
    """
    Retrieve all facet values for a given dataset route.
    
    :param metadata: metadata for the dataset
    :param route: dataset route under the EIA v2 API
    :param api_key: EIA API key
    :return: data containing all facet values
    """
    facets = metadata["facets"]
    facet_values = {}
    rows = []
    for facet in facets:
        # Extract the actual facet ID.
        facet_id = facet["id"]
        facet_route = f"{route}/facet/{facet_id}"
        facet_data = _get_api_request(facet_route, api_key)
        facet_entries = facet_data.get("facets")
        # Build a row for each value associated with this facet.
        for values in facet_entries:
            row = {
                "dataset_id": metadata["dataset_id"],
                "facet_id": facet_id,
                "id": values.get("id"),
                "name": values.get("name"),
                "alias": values.get("alias"),
            }
            rows.append(row)
    df_params = pd.DataFrame(rows)
    return df_params


def run_metadata_extraction(
    category: str,
    api_key: str,
    version_num: str,
    bucket_path: str,
    aws_profile: str,
) -> None:
    """
    Extract and save the full metadata for a given EIA category.

    This function:
    - Retrieves all leaf dataset metadata from the given category.
    - Extracts frequency and metric combinations into a flat index.
    - Collects associated facet values.
    - Saves all files locally and uploads to S3.

    :param category: root category path under EIA v2 API (e.g. "electricity")
    :param api_key: EIA API key used for authentication
    :param version_num: version tag for output paths (e.g. "1.0")
    :param bucket_path: base S3 path where files should be uploaded
    :param aws_profile: AWS profile to use for S3 operations
    """
    leaf_route_data = _get_leaf_route_data(category, api_key)
    if leaf_route_data:
        metadata_entries = []
        for route, data in leaf_route_data.items():
            # Extract metadata.
            metadata = _extract_metadata(data, route, version_num)
            metadata_entries.extend(metadata)
            # Facets are the same for each route.
            sample_metadata = metadata[0]
            # Extract parameter values.
            df_params = _get_facet_values(sample_metadata, route, api_key)
            # Write parameter values to S3 bucket.
            param_file_name = sample_metadata["parameter_values_file"]
            _write_df_to_s3(df_params, param_file_name, bucket_path, aws_profile)
        # Write metadata to S3 bucket.
        df_metadata = pd.DataFrame(metadata_entries)
        metadata_file_path = (
            f"eia_{category}_metadata_index_v{version_num}.csv"
        )
        _write_df_to_s3(df_metadata, metadata_file_path, bucket_path, aws_profile)
    else:
        _LOG.warning("No leaf datasets found under the given root.")


# #############################################################################
# Output handling
# #############################################################################


def _write_df_to_s3(
    df: pd.DataFrame, file_name: str, bucket_path: str, aws_profile: str
) -> None:
    """
    Save the data as a local CSV file and upload it to S3.

    :param df: data to be saved to S3
    :param file_name: local file name for saving
    :param bucket_path: S3 bucket path
    :param aws_profile: AWS CLI profile to use for authentication
    """
    cache_dir = "tmp.download_metadata_cache/"
    local_file_path = os.path.join(cache_dir, file_name)
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    # Save CSV locally.
    df.to_csv(local_file_path, index=False)
    _LOG.debug("Saved CSV locally to: %s", local_file_path)
    # Upload CSV to the specified S3 bucket.
    bucket_file_path = bucket_path + file_name
    hs3.copy_file_to_s3(file_name, bucket_file_path, aws_profile)
    _LOG.debug("Uploaded to S3: %s", bucket_file_path)
    

# #############################################################################
# CLI entry point
# #############################################################################


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Root category path (e.g. electricity, petroleum)",
    )
    parser.add_argument("--api_key", required=True, help="EIA API Key")
    parser.add_argument(
        "--version_num",
        required=True,
        help="Metadata version (e.g. '1.0') used in filenames and S3 paths",
    )
    parser.add_argument(
        "--bucket_path",
        default="s3://causify-data-collaborators/causal_automl/metadata/",
        help="S3 bucket to upload",
    )
    parser.add_argument("--aws_profile", default="ck", help="AWS profile to use")
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    run_metadata_extraction(
        category=args.category,
        api_key=args.api_key,
        version_num=args.version_num,
        bucket_path=args.bucket_path,
        aws_profile=args.aws_profile,
    )


if __name__ == "__main__":
    _main(_parse())
