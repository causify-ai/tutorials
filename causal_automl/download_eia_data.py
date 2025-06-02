"""
Import as:

import causal_automl.download_eia_data as cadoeida
"""

import io
import logging
import os
from typing import Dict, Optional, Tuple

import helpers.hdbg as hdbg
import helpers.hs3 as hs3
import myeia
import pandas as pd

import causal_automl.TutorTask401_EIA_metadata_downloader_pipeline.eia_utils as catemdpeu

_LOG = logging.getLogger(__name__)


# #############################################################################
# EiaDataDownloader
# #############################################################################


class EiaDataDownloader:
    """
    Download historical data from EIA.
    """

    def __init__(self, *, aws_profile: str = "ck") -> None:
        """
        Initialize the EIA data downloader with the API key and AWS profile.

        EIA API key is read from the environment variable.

        :param aws_profile: AWS CLI profile name used for authentication
        """
        hdbg.dassert_in(
            "EIA_API_KEY",
            os.environ,
            msg="EIA_API_KEY is not found in environment variables",
        )
        self._api_key = os.getenv("EIA_API_KEY")
        self._client = myeia.API(token=self._api_key)
        self._aws_profile = aws_profile
        self._metadata_index_by_category: Dict[str, pd.DataFrame] = {}

    def filter_series(
        self,
        df: pd.DataFrame,
        id_: str,
        facets: Dict[str, str],
    ) -> pd.DataFrame:
        """
        Filter and clean a single time series from an EIA dataset.

        This function performs data post-processing:
        - Filter by facet values (e.g., "stateid", "sectorid")
        - Retain only the period and metric column
        - Convert the period column to UTC datetime
        - Set the period as the index and sort chronologically

        :param df: EIA series data
        :param id_: EIA series ID, e.g.,
            "electricity.retail_sales.monthly.price"
        :param facets: facet filters,
            e.g., {"stateid": "WI", "sectorid": "ALL"}
        :return: data of single time series with one facet value per
            facet type

        Example output:
        ```
        period                        price
        2001-01-01T00:00:00+00:00     5.9
        2001-02-01T00:00:00+00:00     5.98
        2001-03-01T00:00:00+00:00     5.93
        ```
        """
        # Filter data with given facet values.
        for key, val in facets.items():
            hdbg.dassert_in(
                key,
                df.columns,
                msg=(
                    f"Facet '{key}' not found in data columns={list(df.columns)}"
                ),
            )
            df = df[df[key] == val]
        if df.empty:
            _LOG.warning("No data remaining after applying facets.")
        # Detect the metric column.
        _, _, _, data_identifier = self._parse_id(id_)
        df = df[["period", data_identifier]]
        # Drop rows with missing value.
        df = df.dropna(subset=[data_identifier])
        if df.empty:
            _LOG.warning("No data remaining after dropping NaN values.")
        # Convert to datetime and index.
        df["period"] = pd.to_datetime(df["period"]).dt.tz_localize("UTC")
        df = df.set_index("period")
        df = df.sort_index()
        return df

    def download_series(
        self,
        id_: str,
        *,
        start_timestamp: Optional[pd.Timestamp] = None,
        end_timestamp: Optional[pd.Timestamp] = None,
        max_rows_per_call: int = 5000,
    ) -> pd.DataFrame:
        """
        Download EIA historical series data.

        This method retrieves the full set of time series linked to an
        EIA identifier, including all combinations of facet values
        (e.g., `stateid`, `sectorid`). When no start and end timestamps are
        passed, the entire time series is downloaded.

        Pagination is handled internally. The `max_rows_per_call` parameter
        controls the page size for each API request, but the method will
        continue fetching until all available data is retrieved.

        :param id_: EIA series ID, e.g.,
            "electricity.retail_sales.monthly.price"
        :param start_timestamp: first observation date
        :param end_timestamp: last observation date
        :param max_rows_per_call: max data rows per API call
        :return: full time series data with all facets

        Example output:
        ```
        period      stateid   stateDescription   sectorid   sectorName
        2020-09     WI        Wisconsin          IND        industrial
        2020-09     WY        Wyoming            ALL        all sectors
        2020-09     IA        Iowa               RES        Residential

        price   price-units
        7.45    cents per kilowatt-hour
        8.55    cents per kilowatt-hour
        12.65   cents per kilowatt-hour
        ```
        """
        # Get base url from metadata index.
        base_url = self._get_metadata_url(id_)
        # Build URL query with API key and timestamps.
        url = catemdpeu.build_full_url(
            base_url,
            self._api_key,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )
        data_chunks = []
        offset = 0
        while True:
            # Construct the paginated URL for the current offset.
            paginated_url = f"{url}&offset={offset}&length={max_rows_per_call}"
            data = self._client.get_response(paginated_url, self._client.header)
            data_chunks.append(data)
            if len(data) < max_rows_per_call:
                # Exit loop when it's the final page of data.
                break
            offset += max_rows_per_call
        if not data_chunks:
            _LOG.warning("No data returned under given id.")
        df = pd.concat(data_chunks, ignore_index=True)
        _LOG.debug("Downloaded %d rows for id=%s", len(df), id_)
        return df

    def _parse_id(self, id_: str) -> Tuple[str, str, str, str]:
        """
        Parse an EIA time series ID into its components.

        EIA time series IDs follow the format:
            <category>.<subroute>.<frequency>.<data_identifier>

        Underscores are converted to dashes to match the EIA API format.

        :param id_: EIA time series ID,
            e.g., "electricity.retail_sales.monthly.price"
        :return:
            - top-level EIA category, e.g., "electricity"
            - subroute in the category, e.g., "retail-sales"
            - reporting frequency, e.g., "monthly"
            - data identifier, e.g., "price"
        """
        id_ = id_.replace("_", "-")
        parts = id_.split(".")
        category = parts[0]
        frequency = parts[-2]
        data_identifier = parts[-1]
        route_parts = parts[1:-2]
        subroute = "/".join(route_parts)
        return category, subroute, frequency, data_identifier

    def _get_latest_metadata_from_s3(self, category: str) -> pd.DataFrame:
        """
        Get the latest versioned metadata index file from S3 for a category.

        :param category: top-level EIA category, e.g., "electricity"
        :return: latest versioned metadata index
        """
        # Get file names from S3 bucket.
        base_dir = "s3://causify-data-collaborators/causal_automl/metadata"
        pattern = f"eia_{category}_metadata_original_v*"
        files = hs3.listdir(
            dir_name=base_dir,
            pattern=pattern,
            only_files=True,
            use_relative_paths=False,
            aws_profile=self._aws_profile,
            maxdepth=1,
        )
        if not files:
            raise FileNotFoundError(
                f"No metadata index file found for category: '{category}' in S3."
            )
        # Get latest file version.
        files.sort(reverse=True)
        s3_path = f"s3://{files[0]}"
        # Load latest metadata index file from S3.
        csv_str = hs3.from_file(s3_path, aws_profile=self._aws_profile)
        df = pd.read_csv(io.StringIO(csv_str))
        return df

    def _get_metadata_url(self, id_: str) -> str:
        """
        Get base URL for given series ID from the metadata index.

        :param id_: EIA time series ID,
            e.g., "electricity.retail_sales.monthly.price"
        :return: base API URL with frequency and metric, excluding facet values,
            e.g., "https://api.eia.gov/v2/electricity/retail-sales?api_key={API_KEY}&frequency=monthly&data[0]=revenue"
        """
        category, _, _, _ = self._parse_id(id_)
        # Load latest metadata index file from S3.
        if category not in self._metadata_index_by_category:
            self._metadata_index_by_category[category] = (
                self._get_latest_metadata_from_s3(category)
            )
        df = self._metadata_index_by_category[category]
        # Filter for exact ID match.
        match = df[df["id"] == id_]
        if match.empty:
            raise ValueError(f"Invalid ID: '{id_}'")
        base_url: str = match.iloc[0]["url"]
        return base_url
