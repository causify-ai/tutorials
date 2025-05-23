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
import ratelimit

import causal_automl.TutorTask401_EIA_metadata_downloader_pipeline.eia_utils as catemdpeu

_LOG = logging.getLogger(__name__)


# #############################################################################
# EiaDataDownloader
# #############################################################################


class EiaDataDownloader:
    """
    Download historical data from EIA.
    """

    def __init__(
        self, *, api_key: Optional[str] = None, aws_profile: Optional[str] = "ck"
    ) -> None:
        """
        Initialize the EIA data downloader with the API key.

        If no EIA API key is passed as a parameter, it is read from the
        environment variable.

        :param api_key: EIA API key
        :param aws_profile: AWS CLI profile name used for authentication
        """
        self._api_key = api_key or os.getenv("EIA_API_KEY")
        if not self._api_key:
            raise ValueError("EIA API key is required")
        self._client = myeia.API(token=self._api_key)
        self._aws_profile = aws_profile
        self.base_url = "https://api.eia.gov/v2/"

    def filter_series(
        self,
        df: pd.DataFrame,
        id_: str,
        facets: Dict[str, str],
    ) -> pd.DataFrame:
        """
        Filter and clean a single time series from an EIA dataset.

        Apply facet filters (e.g., state, sector) to select one unique
        series, drop missing values, and convert the time column to a
        UTC-indexed datetime format.

        :param df: EIA series data
        :param id_: EIA series ID, e.g.,
            "electricity.retail_sales.monthly.price"
        :param facets: facet filters, 
            e.g., {"stateid": "WI", "sectorid": "ALL"}
        :return: data of single time series with one facet value per
            facet type
        """
        # Filter data with given facet values.
        for key, val in facets.items():
            hdbg.dassert_in(
                key,
                df.columns,
                "Facet '%s' not found in data columns=%s",
                key,
                list(df.columns),
            )
            df = df[df[key] == val]
        # Detect the metric column.
        _, data_identifier = self._parse_id(id_)
        # Drop rows with missing value.
        df = df.dropna(subset=[data_identifier])
        if df.empty:
            _LOG.warning("No data remaining after applying facets.")
        # Convert to datetime index.
        df["period"] = pd.to_datetime(df["period"])
        df = df.rename(columns={"period": "period (UTC)"})
        df = df.set_index("period (UTC)")
        df.index = df.index.tz_localize("UTC")
        return df

    @ratelimit.sleep_and_retry
    @ratelimit.limits(calls=60, period=60)
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

        :param id_: EIA series ID, e.g.,
            "electricity.retail_sales.monthly.price"
        :param start_timestamp: first observation date
        :param end_timestamp: last observation date
        :param max_rows_per_call: max data rows per api call
        :return: full time series data with all facets
        """
        # Get base url from metadata index.
        base_url = self._get_metadata_url(id_)
        # Build URL query with api key and timestamps.
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
                # Exit loop when its the final page of data.
                break
            offset += max_rows_per_call
        if not data_chunks:
            _LOG.warning("No data returned under given id.")
        df = pd.concat(data_chunks, ignore_index=True)
        _LOG.debug("Downloaded %d rows for id=%s", len(df), id_)
        return df

    def _parse_id(self, id_: str) -> Tuple[str, str]:
        """
        Parse an EIA time series ID into its components.

        :param id_: EIA time series ID,
            e.g., "electricity.retail_sales.monthly.price"
        :return:
            - top-level EIA category, e.g., "electricity"
            - data identifier, e.g., "price"
        """
        id_ = id_.replace("_", "-")
        parts = id_.split(".")
        category = parts[0]
        data_identifier = parts[-1]
        return category, data_identifier

    def _get_latest_metadata_s3_path(self, category: str) -> str:
        """
        Get the latest versioned metadata file S3 path for a given category.

        :param category: top-level EIA category, e.g., "electricity"
        :return: full S3 path to the latest version of the metadata CSV
            e.g., "eia_electricity_metadata_original_v2.0.csv"
        """
        # Get file names from s3 bucket.
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
        return s3_path

    def _get_metadata_url(self, id_: str) -> str:
        """
        :param id_: EIA time series ID,
            e.g., "electricity.retail_sales.monthly.price"
        :param category: top-level EIA category, e.g., "electricity"
        :return: base API URL with frequency and metric, excluding facet values,
            e.g., "https://api.eia.gov/v2/electricity/retail-sales?api_key={API_KEY}&frequency=monthly&data[0]=revenue"
        """
        category, _ = self._parse_id(id_)
        # Load latest metadata index file from s3.
        s3_path = self._get_latest_metadata_s3_path(category)
        csv_str = hs3.from_file(s3_path, aws_profile=self._aws_profile)
        df = pd.read_csv(io.StringIO(csv_str))
        # Filter for exact ID match.
        match = df[df["id"] == id_]
        if match.empty:
            raise ValueError(f"Invalid id: '{id_}'")
        row = match.iloc[0]
        base_url = str(row["url"])
        return base_url
