#!/usr/bin/env python3
"""
Fetch metadata from the EIA v2 API and upload it to S3.

Usage:
> python fetch_eia_metadata.py --category electricity --api_key <API_KEY> --aws_profile

This script traverses the EIA v2 API under a specified category and collects all time series
metadata. It then writes the extracted metadata to an S3 bucket in CSV format.

Arguments:
    --category       Root category path under the EIA v2 API.
    --api_key        EIA API key used to authenticate requests.
    --aws_profile    AWS CLI profile to use for writing the output to S3. Defaults to "ck".
"""

import argparse
import csv
import io
import logging
from typing import Any, Dict, List

import helpers.hdbg as hdbg
import helpers.hparser as hparser
import helpers.hs3 as hs3
import requests

_LOG = logging.getLogger(__name__)

# #############################################################################
# API interaction.
# #############################################################################


def _get_api_request(route: str, api_key: str) -> Dict[str, Any]:
    """
    Retrieve JSON data from a given EIA v2 API route.

    :param route: endpoint path like "electricity/retail-sales"
    :param api_key: EIA API key
    :return: content from the EIA API response
    """
    # Build the full API request URL.
    base_url = "https://api.eia.gov/v2"
    url = f"{base_url}/{route}?api_key={api_key}"
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
    base_browser_url = f"https://www.eia.gov/opendata/browser/{route}"
    metadata = {
        "url": base_browser_url,
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "frequency": data.get("frequency"),
        "facets": data.get("facets"),
        "data": data.get("data"),
        "start_period": data.get("startPeriod"),
        "end_period": data.get("endPeriod"),
        "default_date_format": data.get("defaultDateFormat"),
        "default_frequency": data.get("defaultFrequency"),
    }
    return metadata


def _collect_leaf_metadata(route: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Recursively traverse the API tree and collect metadata from all leaf
    routes.

    :param route: root category route
    :param api_key: EIA API key
    :return: metadata extracted from all leaf endpoints
    """
    # Get the API response for the current route.
    data = _get_api_request(route, api_key)
    if not data:
        # Check if response is empty.
        return []
    # Get child routes if present and recurse into each.
    children = data.get("routes", [])
    metadata_list = []
    if children:
        # Recurse to get leaf node.
        for child in children:
            child_id = child["id"]
            child_route = f"{route}/{child_id}"
            metadata_list.extend(_collect_leaf_metadata(child_route, api_key))
    else:
        # This is a leaf route, extract and append metadata.
        metadata = _extract_metadata(data, route)
        metadata_list.append(metadata)
    return metadata_list


# #############################################################################
# Output handling.
# #############################################################################


def _write_csv_to_s3(
    metadata_list: List[Dict], filename: str, aws_profile: str
) -> None:
    """
    Write metadata to an S3 bucket in CSV format.

    :param metadata_list: metadata to be written
    :param filename: full S3 URI where CSV should be saved
    :param aws_profile: AWS CLI profile to use for authentication
    """
    # Prepare CSV content in memory.
    fieldnames = list(metadata_list[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in metadata_list:
        writer.writerow(row)
    # Upload the CSV string to the specified S3 bucket.
    csv_str = buffer.getvalue()
    hs3.to_file(csv_str, filename, mode="wb", aws_profile=aws_profile)


# #############################################################################
# CLI entry point.
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
    _LOG.debug("Traversing EIA hierarchy under category='%s'...", args.category)
    # Fetch metadata.
    metadata_list = _collect_leaf_metadata(args.category, args.api_key)
    _LOG.debug("Found %d leaf datasets.", len(metadata_list))
    if metadata_list:
        file_name = f"eia_{args.category}_metadata.csv"
        output_path = (
            f"s3://causify-data-collaborators/causal_automl/metadata/{file_name}"
        )
        _LOG.debug("Writing metadata to: %s", output_path)
        # Write to S3 bucket.
        _write_csv_to_s3(metadata_list, output_path, args.aws_profile)
    else:
        # Skip if no metadata found.
        _LOG.warning("No leaf datasets found under category='%s'.", args.category)


if __name__ == "__main__":
    _main(_parse())
