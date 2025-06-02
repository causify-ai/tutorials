"""
Import as:

import causal_automl.download_gridstatus_data as cadogrda
"""

import logging
import os
import time
from typing import Dict, Optional, Union

import gridstatusio
import helpers.hdbg as hdbg
import pandas as pd
import ratelimit

_LOG = logging.getLogger(__name__)


# #############################################################################
# GridstatusDataDownloader
# #############################################################################


class GridstatusDataDownloader:
    """
    Download historical data from GridStatus.io.
    """

    def __init__(self) -> None:
        """
        Initialize the GridStatus data downloader with the API key.
        """
        hdbg.dassert_in(
            "GRIDSTATUS_API_KEY",
            os.environ,
            msg="GRIDSTATUS_API_KEY is not found in environment variables",
        )
        api_key = os.getenv("GRIDSTATUS_API_KEY")
        self._client = gridstatusio.GridStatusClient(api_key=api_key)

    @ratelimit.sleep_and_retry
    @ratelimit.limits(calls=60, period=60)
    def download_series(
        self,
        id_: str,
        start_timestamp: Optional[Union[str, pd.Timestamp]] = None,
        end_timestamp: Optional[Union[str, pd.Timestamp]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Download historical series data.

        When no start and end timestamps are passed, the entire time series is downloaded.

        Example of a returned series:

        ```
        interval_start_utc          interval_end_utc            region          market
        2010-01-01 08:00:00+00:00   2010-01-01 09:00:00+00:00   AS_CAISO        DAM
        2010-01-01 08:00:00+00:00   2010-01-01 09:00:00+00:00   AS_CAISO_EXP    DAM
        /
        non_spinning_reserves
        0.0
        0.5
        ```

        :param id_: Gridstatus series identifier (e.g., "caiso_as_prices.spinning_reserves")
        :param start_timestamp: first observation timestamp
            (e.g., "2010-01-01 08:00:00+00:00" or pd.Timestamp("2023-04-01 01:00:00"))
        :param end_timestamp: last observation timestamp
        :return: relevant Gridstatus series data
        """
        # Build request parameters.
        id_dataset, name_series = id_.split(".", 1)
        request_kwargs: Dict[str, str] = {}
        if start_timestamp is not None:
            request_kwargs["start"] = start_timestamp
        if end_timestamp is not None:
            request_kwargs["end"] = end_timestamp
        # Start attempts.
        attempt = 1
        max_attempts = 4
        err_msgs: Dict[str, str] = {}
        while attempt <= max_attempts:
            try:
                # Download the data for the dataset.
                df = self._client.get_dataset(
                    dataset=id_dataset,
                    columns=[name_series],
                    **request_kwargs,
                )
            except Exception as err:
                msg = str(err)
                if msg.startswith("Error 5"):
                    _LOG.error("Attempt %d: %s Retrying...", attempt, msg)
                    # Wait before retrying.
                    time.sleep(10)
                else:
                    raise
                err_msgs[f"Attempt {attempt}"] = msg
                attempt += 1
                continue
            # Log success and return.
            _LOG.info(
                "Downloaded series %s with %d records",
                id_,
                len(df),
            )
            return df
        raise RuntimeError(
            f"Failed to fetch after {max_attempts} attempts. Errors per run: {err_msgs}"
        )

    def filter_series(
        self,
        df: pd.DataFrame,
        id_: str,
        filters: Dict[str, str],
    ) -> pd.DataFrame:
        """
        Filter out a single time series from a Gridstatus dataset.

        - Apply single filters across columns (e.g., `region`, `market`)
        - Drop NaN values
        - Set the end timestamp as index

        E.g.,

        Input series (caiso_as_prices.non_spinning_reserves):
        ```
        interval_start_utc          interval_end_utc            region          market
        2022-01-01 08:00:00+00:00   2022-01-01 09:00:00+00:00   AS_CAISO        DAM
        2022-01-01 08:00:00+00:00   2022-01-01 09:00:00+00:00   AS_CAISO_EXP    DAM
        2022-01-01 08:00:00+00:00   2022-01-01 09:00:00+00:00   AS_NP26         DAM
        2022-01-01 08:00:00+00:00   2022-01-01 09:00:00+00:00   AS_NP26_EXP     DAM
        2022-01-01 08:00:00+00:00   2022-01-01 09:00:00+00:00   AS_SP26         DAM
        ...                         ...                         ...             ...
        /
        non_spinning_reserves
        0.00
        0.15
        0.00
        0.00
        0.00
        ...
        ```
        Output series (with filters - {"region": "AS_CAISO_EXP", "market": "DAM"})):
        ```
                                        non_spinning_reserves
        interval_end_utc
        2022-01-01 09:00:00+00:00                   0.15
        2022-01-01 10:00:00+00:00                   0.15
        2022-01-01 11:00:00+00:00                   0.15
        2022-01-01 12:00:00+00:00                   0.15
        2022-01-01 13:00:00+00:00                   0.15
        ...                                          ...
        ```

        :param df: data series to filter
        :param id_: series identifier (e.g., "caiso_as_prices.spinning_reserves")
        :param filters: filters to apply on the dataset
            (e.g., {"region": "AS_CAISO_EXP", "market": "DAM"})
        :return: filtered series
        """
        # Filter data.
        filtered_data = df.copy()
        for k, v in filters.items():
            hdbg.dassert_in(
                k,
                filtered_data.columns,
                "%s not found in columns: %s",
                k,
                list(filtered_data.columns),
            )
            filtered_data = filtered_data[filtered_data[k] == v]
        if filtered_data.empty:
            _LOG.warning("No data remaining after applying filters")
        # Find the series name.
        name_series = id_.split(".", 1)[1]
        # Drop missing value rows.
        filtered_data = filtered_data.dropna(subset=[name_series])
        if filtered_data.empty:
            _LOG.warning("No data remaining after dropping NaN values")
        filtered_data = filtered_data[["interval_end_utc", name_series]]
        filtered_data = filtered_data.set_index("interval_end_utc")
        filtered_data = filtered_data.sort_index()
        return filtered_data
