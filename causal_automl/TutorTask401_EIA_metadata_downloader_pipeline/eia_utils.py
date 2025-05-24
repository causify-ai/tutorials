"""
Import as:

import causal_automl.TutorTask401_EIA_metadata_downloader_pipeline.eia_utils as catemdpeu
"""

import logging
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import requests

_LOG = logging.getLogger(__name__)


# #############################################################################
# EiaMetadataDownloader
# #############################################################################


class EiaMetadataDownloader:
    """
    Extract EIA time series metadata and facet values.
    """

    def __init__(
        self,
        category: str,
        api_key: str,
        version_num: str,
        *,
        base_url: str = "https://api.eia.gov/v2",
    ) -> None:
        """
        Initialize the metadata downloader.

        :param category: root category path under the EIA v2 API (e.g.,
            "electricity")
        :param api_key: EIA API key
        :param version_num: version tag for output paths (e.g., "1.0")
        :param base_url: base URL for the EIA v2 API
        """
        self._category = category
        self._api_key = api_key
        self._version_num = version_num
        self._base_url = base_url

    def run_metadata_extraction(
        self,
    ) -> Tuple[pd.DataFrame, List[Tuple[pd.DataFrame, str]]]:
        """
        Extract metadata and facet values for a given EIA category.

        :return: flattened metadata and corresponding facet tables with
            file paths
        """
        metadata_entries: List[Dict[str, Any]] = []
        param_entries: List[Tuple[pd.DataFrame, str]] = []
        df_metadata = pd.DataFrame()
        leaf_route_data = self._get_leaf_route_data()
        if leaf_route_data:
            for route, data in leaf_route_data.items():
                # Extract metadata.
                metadata = self._extract_metadata(data, route)
                metadata_entries.extend(metadata)
                # Facets are the same for each route.
                sample_metadata = metadata[0]
                # Extract parameter values.
                df_params = self._get_facet_values(sample_metadata, route)
                param_entries.append(
                    (df_params, sample_metadata["parameter_values_file"])
                )
            df_metadata = pd.DataFrame(metadata_entries)
        else:
            _LOG.warning("No leaf datasets found under the given root.")
        return df_metadata, param_entries

    def _get_api_request(self, route: str) -> Dict[str, Any]:
        """
        Retrieve JSON data from a given EIA v2 API route.

        This function sends a GET request to the specified EIA v2 API endpoint
        and returns the parsed content from the "response" key.

        :param route: endpoint path like "electricity/retail-sales"
        :return: content from the EIA API response

        Example output:
        ```
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
        ```
        """
        # Build the full API request URL.
        url = f"{self._base_url}/{route}?api_key={self._api_key}"
        # Send HTTP GET request to the EIA API.
        response = requests.get(url, timeout=20)
        # Parse JSON content.
        json_data = response.json()
        # Get response from parsed payload.
        data: Dict[str, Any] = {}
        data = json_data.get("response", {})
        return data

    def _get_leaf_route_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Traverse the API tree and collect metadata from all leaf routes.

        This function performs a breadth-first traversal over all sub-routes beginning at
        `root_route`. For each route that has no children (i.e., a leaf), it fetches and stores
        the associated metadata.

        :return: all leaf routes and their data payloads

        Example output:
        ```
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
        ```
        """
        # Create a queue to hold routes to explore.
        queue = [self._category]
        leaf_route_data = {}
        # Traverse and collect all leaf routes.
        while queue:
            current_route = queue.pop(0)
            data = self._get_api_request(current_route)
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

    def _extract_metadata(
        self, data: Dict[str, Any], route: str
    ) -> List[Dict[str, Any]]:
        """
        Extract and flatten relevant metadata fields from a single API
        response.

        For each frequency and metric combination in the dataset, construct a flat
        metadata record containing API query details, dataset properties, frequency
        info, metric info, and associated file paths.

        :param data: API response content for a leaf endpoint
        :param route: full route path used to access this response
        :return: flattened metadata fields

        Example output:
        ```
        [
            {
                "url": "https://api.eia.gov/v2/electricity/retail-sales?api_key={API_KEY}&frequency=monthly&data[0]=revenue",
                "id": "electricity.retail_sales.monthly.revenue",
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
        ```
        """
        frequencies = data.get("frequency", [])
        metrics = data.get("data", {})
        flattened_metadata = []
        for frequency in frequencies:
            for metric_id, metric_info in metrics.items():
                # Clean up IDs for use in CSVs or DBs.
                frequency_id = frequency.get("id")
                metric_id_clean = metric_id.replace("-", "_")
                route_clean = route.replace("-", "_").replace("/", ".")
                dataset_id_clean = route_clean.split(".")[-1]
                # Construct a placeholder API URL.
                url = (
                    f"{self._base_url}/{route}"
                    f"?api_key={{API_KEY}}"
                    f"&frequency={frequency_id}"
                    f"&data[0]={metric_id}"
                )
                # Determine parameter CSV path for associated facet values.
                param_file_path = f"eia_parameters_v{self._version_num}/{dataset_id_clean}_parameters.csv"
                # Flattened metadata row for one frequency and metric combination.
                metadata = {
                    "url": url,
                    "id": f"{route_clean}.{frequency_id}.{metric_id_clean}",
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

    def _get_facet_values(
        self, metadata: Dict[str, Any], route: str
    ) -> pd.DataFrame:
        """
        Retrieve all facet values for a given dataset route.

        :param metadata: metadata for the dataset
        :param route: dataset route under the EIA v2 API
        :return: data containing all facet values
        """
        facets = metadata["facets"]
        rows = []
        for facet in facets:
            # Extract the actual facet ID.
            facet_id = facet["id"]
            facet_route = f"{route}/facet/{facet_id}"
            facet_data = self._get_api_request(facet_route)
            facet_entries = facet_data.get("facets", {})
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


def build_full_url(
    base_url: str,
    api_key: str,
    facet_input: Dict[str, str],
) -> str:
    """
    Build a full EIA v2 API URL by appending one facet value per facet type.

    This modifies the base metadata URL to point to the actual time series
    data endpoint.

    :param base_url: base API URL with frequency and metric, excluding
        facet values,
        e.g., "https://api.eia.gov/v2/electricity/retail-sales?api_key={API_KEY}&frequency=monthly&data[0]=revenue"
    :param api_key: EIA API key, e.g., "abcd1234xyz"
    :param facet_input: specified facet values, e.g., {"stateid": "KS", "sectorid": "COM"}
    :return: full EIA API URL with all required facet parameters,
        e.g, "https://api.eia.gov/v2/electricity/retail-sales/data?api_key=abcd1234xyz&frequency=monthly&data[0]=price&facets[stateid][]=KS&facets[sectorid][]=OTH"
    """
    base_url = base_url.replace("?", "/data?")
    url = base_url.replace("{API_KEY}", api_key)
    query_parts = []
    for facet_id, value in facet_input.items():
        query_parts.append(f"&facets[{facet_id}][]={value}")
    full_url = url + "".join(query_parts)
    return full_url


def plot_distribution(df_metadata: pd.DataFrame, column: str, title: str) -> None:
    """
    Plot a distribution count for a specified metadata column.

    :param df_metadata: metadata index data
    :param column: column to group and count values by (e.g.,
        'frequency_id', 'data_units')
    :param title: title for the plot
    """
    if column not in df_metadata.columns:
        raise ValueError(f"Column '{column}' not found in metadata index.")
    counts = df_metadata[column].value_counts()
    ax = counts.plot(kind="bar", figsize=(8, 4), title=title)
    ax.set_xlabel(column.replace("_", " ").title())
    ax.set_ylabel("Count")
    ax.grid(True)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
