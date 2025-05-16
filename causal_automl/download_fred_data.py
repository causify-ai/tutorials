"""
Import as:

import causal_automl.download_fred_data as cadofrda
"""

import logging as log
import os
import time
from typing import Optional

import fredapi
import helpers.hdbg as hdbg
import pandas as pd
import ratelimit

_LOG = log.getLogger(__name__)


# #############################################################################
# FredDataDownloader
# #############################################################################


class FredDataDownloader:
    """
    Download historical data from FRED.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the FRED data downloader with the API key.

        If no FRED API key is passed as a parameter, it is read from the
        environment variable.

        :param api_key: FRED API key
        """
        key = api_key or os.getenv("FRED_API_KEY")
        if not key:
            raise ValueError("FRED API key is required")
        self._client = fredapi.Fred(api_key=key)

    @ratelimit.sleep_and_retry
    @ratelimit.limits(calls=60, period=60)
    def download_series(
        self,
        id_: str,
        start_timestamp: Optional[pd.Timestamp] = None,
        end_timestamp: Optional[pd.Timestamp] = None,
        frequency: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Download historical series data.

        When no start and end timestamps are passed, the entire time series is downloaded.
        If no frequency is passed, the highest available frequency is downloaded.

        Example of a returned series:

        ```
                          GDP
        2019-10-01  21933.217
        2020-01-01  21727.657
        2020-04-01  19935.444
        ```

        :param id_: FRED series identifier (e.g., "GDP")
        :param start_timestamp: first observation date
        :param end_timestamp: last observation date
        :param frequency: series data frequency
            - "q": quarter
            - "sa": semi-annual
            - "a": annual
        :return: relevant FRED series data
        """
        # Validate the passed frequency value.
        valid_freqs = ["q", "sa", "a"]
        if frequency is not None:
            hdbg.dassert_in(
                frequency,
                valid_freqs,
                "Invalid frequency '%s'.",
                frequency,
            )
        # Set args.
        loading_kwargs = {}
        if start_timestamp is not None:
            loading_kwargs["observation_start"] = start_timestamp
        if end_timestamp is not None:
            loading_kwargs["observation_end"] = end_timestamp
        if frequency is not None:
            loading_kwargs["frequency"] = frequency
        attempt = 1
        max_attempts = 4
        err_msgs = {}
        # Start attempts.
        while attempt <= max_attempts:
            try:
                # Download the data for the series.
                series = self._client.get_series(
                    id_,
                    **loading_kwargs,
                )
            except Exception as err:
                if "Internal Server Error" in str(err):
                    _LOG.error("Attempt %s: %s Retrying...", attempt, err)
                    # Wait before retrying.
                    time.sleep(10)
                elif "Too Many Requests" in str(err):
                    # Retry after exponential backoff.
                    backoff = 4**attempt
                    _LOG.error(
                        "Attempt %d: %s Retrying after %ds... ",
                        attempt,
                        err,
                        backoff,
                    )
                    time.sleep(backoff)
                    continue
                else:
                    raise
                err_msgs[f"Attempt {attempt}"] = str(err)
                attempt += 1
                continue
            # Package the output.
            df = series.to_frame(name=id_)
            _LOG.info(
                "Downloaded series %s with %d records",
                id_,
                len(df),
            )
            return df
        raise RuntimeError(
            f"Failed to fetch after {max_attempts} attempts. Errors per run: {err_msgs}"
        )
