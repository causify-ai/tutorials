#!/usr/bin/env python3
"""
Download metadata from the EIA v2 API and upload it to S3.

Usage:
> python fetch_eia_metadata.py --category <CATEGORY> --api_key <API_KEY> --version_num <VERSION_NUM>

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

    :param data: API response content for a leaf endpoint
    :param route: full route path used to access this response
    :param version_num: version number of output paths
    :return: flattened metadata fields
    """
    url = f"{BASE_URL}/{route}?api_key="
    dataset_id = data.get("id")
    dataset_id_clean = dataset_id.replace("-", "_")
    param_file_path = (
        f"eia_parameters_v{version_num}/{dataset_id_clean}_parameters.csv"
    )
    frequencies = data.get("frequency", [])
    metrics = data.get("data", {})
    flattened_metadata = []
    for frequency in frequencies:
        freq_id = frequency.get("id")
        for metric_id in metrics.keys():
            metadata = {
                "url": url,
                "id": dataset_id,
                "name": data.get("name"),
                "description": data.get("description"),
                "frequency": freq_id,
                "facets": data.get("facets"),
                "data": metric_id,
                "start_period": data.get("startPeriod"),
                "end_period": data.get("endPeriod"),
                "default_date_format": data.get("defaultDateFormat"),
                "default_frequency": data.get("defaultFrequency"),
                "parameter_values_file": param_file_path,
            }
            flattened_metadata.append(metadata)
    return flattened_metadata


def _get_leaf_route_data(
    root_route: str, api_key: str
) -> Dict[str, Dict[str, Any]]:
    """
    Traverse the API tree and collect metadata from all leaf routes.

    :param root_route: root category route
    :param api_key: EIA API key
    :return: all leaf route and its data payload
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
        facet_values[facet_id] = facet_data.get("facets", {})
        # Build a row for each value associated with this facet.
        for values in facet_values[facet_id]:
            row = {
                "dataset_id": metadata["id"],
                "facet_id": facet_id,
                "id": values.get("id"),
                "name": values.get("name"),
                "alias": values.get("alias"),
            }
            rows.append(row)
    df_params = pd.DataFrame(rows)
    return df_params


# #############################################################################
# Output handling
# #############################################################################


def _write_df_to_s3(
    df: pd.DataFrame, file_name: str, aws_profile: str
) -> None:
    """
    Write metadata to an S3 bucket in CSV format.

    :param df: data to be saved to S3
    :param file_name: full S3 URI where CSV should be saved
    :param aws_profile: AWS CLI profile to use for authentication
    """
    # Convert DataFrame to CSV String.
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    csv_str = buffer.getvalue()
    # Upload the CSV string to the specified S3 bucket.
    csv_str = buffer.getvalue()
    hs3.to_file(csv_str, file_name, mode="wb", aws_profile=aws_profile)


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
    leaf_route_data = _get_leaf_route_data(args.category, args.api_key)
    if leaf_route_data:
        metadata_entries = []
        for route, data in leaf_route_data.items():
            # Extract metadata.
            metadata = _extract_metadata(data, route, args.version_num)
            metadata_entries.extend(metadata)
            # Facets are the same for each route.
            sample_metadata = metadata[0]
            # Extract parameter values.
            df_params = _get_facet_values(sample_metadata, route, args.api_key)
            # Write parameter values to S3 bucket.
            param_file_name = sample_metadata["parameter_values_file"]
            param_file_path = args.bucket_path + param_file_name
            _LOG.debug("Writing parameter values to: %s", param_file_path)
            _write_df_to_s3(df_params, param_file_path, args.aws_profile)
        # Write metadata to S3 bucket.
        df_metadata = pd.DataFrame(metadata_entries)
        metadata_file_path = (
            f"{args.bucket_path}eia_{args.category}_metadata_index_v{args.version_num}.csv"
        )
        _LOG.debug("Writing metadata to: %s", metadata_file_path)
        _write_df_to_s3(df_metadata, param_file_path, args.aws_profile)
    else:
        _LOG.warning("No leaf datasets found under the given root.")
    

if __name__ == "__main__":
    _main(_parse())
