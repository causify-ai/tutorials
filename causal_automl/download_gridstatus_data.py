"""
Import as:

import causal_automl.download_gridstatus_data as cadogrda
"""

import logging
import os
import time
from typing import Dict, Optional

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

        If no API key is passed as a parameter, it is read from the
        GRIDSTATUS_API_KEY environment variable.

        :param api_key: GridStatus API key
        """
        hdbg.dassert_in(
            "GRIDSTATUS_API_KEY",
            os.environ,
            msg="GRIDSTATUS_API_KEY is not found in environment variables",
        )
        api_key = os.getenv("GRIDSTATUS_API_KEY")
        key = api_key or os.getenv("GRIDSTATUS_API_KEY")
        if not key:
            raise ValueError("GridStatus API key is required")
        self._client = gridstatusio.GridStatusClient(api_key=key)

    @ratelimit.sleep_and_retry
    @ratelimit.limits(calls=60, period=60)
    def download_series(
        self,
        id_: str,
        start_timestamp: Optional[pd.Timestamp] = None,
        end_timestamp: Optional[pd.Timestamp] = None,
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

        :param id_: GridStatus dataset identifier (e.g., "caiso_as_prices.spinning_reserves")
        :param start_timestamp: first observation timestamp (e.g., "2010-01-01 08:00:00+00:00")
        :param end_timestamp: last observation timestamp
        :return: relevant GridStatus series data
        """
        # Build request parameters.
        id_series, name_series = id_.split(".", 1)
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
                    dataset=id_series,
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
                "Downloaded dataset %s with %d records",
                id_,
                len(df),
            )
            return df
        raise RuntimeError(
            f"Failed to fetch after {max_attempts} attempts. Errors per run: {err_msgs}"
        )
