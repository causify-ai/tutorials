#!/usr/bin/env python3
"""
Download metadata from the EIA v2 API and upload it to S3.

Usage:
> python fetch_eia_metadata.py --category electricity --api_key <API_KEY>

This script traverses the EIA v2 API under a specified category, collects all time series 
metadata, and writes the metadata and associated parameter values to an S3 bucket in CSV 
format.

Arguments:
    --category       Root category path under the EIA v2 API.
    --api_key        EIA API key used to authenticate requests.
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


def _extract_metadata(data: Dict[str, Any], route: str) -> Dict[str, Any]:
    """
    Extract relevant metadata fields from a single API response.

    :param data: API response content for a leaf endpoint
    :param route: full route path used to access this response
    :return: metadata fields
    """
    url = f"{BASE_URL}/{route}?api_key="
    dataset_id = data.get("id")
    dataset_id_clean = dataset_id.replace("-", "_")
    param_file_path = f"s3://causify-data-collaborators/causal_automl/eia_parameters/{dataset_id_clean}_parameters.csv"
    metadata = {
        "url": url,
        "id": dataset_id,
        "name": data.get("name"),
        "description": data.get("description"),
        "frequency": data.get("frequency"),
        "facets": data.get("facets"),
        "data": data.get("data"),
        "start_period": data.get("startPeriod"),
        "end_period": data.get("endPeriod"),
        "default_date_format": data.get("defaultDateFormat"),
        "default_frequency": data.get("defaultFrequency"),
        "parameter_values_file": param_file_path,
    }
    return metadata


def _get_all_leaf_routes(root_route: str, api_key: str) -> List[str]:
    """
    Traverse the API tree and collect metadata from all leaf routes.

    :param root_route: root category route
    :param api_key: EIA API key
    :return: all route paths of all leaf datasets under the root
    """
    # Create a queue to hold routes to explore.
    queue = [root_route]
    leaf_routes = []
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
            leaf_routes.append(current_route)
    return leaf_routes


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
    for facet_id in facets:
        # Extract the actual facet ID.
        facetid = facet_id["id"]
        # Build the URL to query all values for this facet.
        url = f"{BASE_URL}/{route}/facet/{facetid}?api_key={api_key}"
        # Query the EIA API.
        response = requests.get(url, timeout=20)
        # Parse the response for facet values.
        entry = response.json().get("response", {}).get("facets", {})
        facet_values[facetid] = entry
        # Build a row for each value associated with this facet.
        for values in entry:
            row = {
                "dataset_id": metadata["id"],
                "facet_id": facetid,
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
    df: pd.DataFrame, filename: str, aws_profile: str
) -> None:
    """
    Write metadata to an S3 bucket in CSV format.

    :param df: data to be saved to S3
    :param filename: full S3 URI where CSV should be saved
    :param aws_profile: AWS CLI profile to use for authentication
    """
    # Convert DataFrame to CSV String.
    buffer = io.StringIO()
    dataframe.to_csv(buffer, index=False)
    csv_str = buffer.getvalue()
    # Upload the CSV string to the specified S3 bucket.
    csv_str = buffer.getvalue()
    hs3.to_file(csv_str, filename, mode="wb", aws_profile=aws_profile)


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
    parser.add_argument("--aws_profile", default="ck", help="AWS profile to use")
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    leaf_routes = _get_all_leaf_routes(args.category, args.api_key)
    _LOG.debug("Found %d leaf datasets.", len(leaf_routes))
    if leaf_routes:
        metadata_entries = []
        for route in leaf_routes:
            data = _get_api_request(route, args.api_key)
            # Extract metadata.
            metadata = _extract_metadata(data, route)
            metadata_entries.append(metadata)
            # Extract parameter values.
            df_params = _get_facet_values(metadata, route, args.api_key)
            # Write parameter values to S3 bucket.
            param_path = metadata["parameter_values_file"]
            _LOG.debug("Writing parameter values to: %s", param_path)
            _write_df_to_s3(df_params, param_path, args.aws_profile)
        # Convert metadata to DataFrame.
        df_metadata = pd.DataFrame(metadata_entries)
        # Write metadata to S3 bucket.
        file_name = f"eia_{args.category}_metadata_index.csv"
        output_path = (
            f"s3://causify-data-collaborators/causal_automl/metadata/{file_name}"
        )
        _LOG.debug("Writing metadata to: %s", output_path)
        _write_df_to_s3(df_metadata, output_path, args.aws_profile)
    else:
        _LOG.warning("No leaf datasets found under the given root.")

if __name__ == "__main__":
    _main(_parse())
