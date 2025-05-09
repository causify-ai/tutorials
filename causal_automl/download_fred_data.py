import logging
import os
import time
from typing import Optional

import fredapi
import pandas as pd
import ratelimit

_LOG = logging.getLogger(__name__)


# #############################################################################
# FredDataDownloader
# #############################################################################


class FredDataDownloader:
    """
    Load historical data from FRED.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the FRED data downloader with the API key.

        If no FRED API key is passed as a parameter, it is read from the
        environment variables.

        :param api_key: FRED api key
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
    ) -> pd.DataFrame:
        """
        Download historical data.

        When no start and end timestamps are passed, the entire time series is downloaded.
        Valid frequencies are: 'q' (quarter), 'sa' (semi-annual), 'a' (annual).
        If invalid frequencies are passed, the frequency parameter is automatically dropped.

        Example of a returned series,

                          GDP
        2019-10-01  21933.217
        2020-01-01  21727.657
        2020-04-01  19935.444

        :param id_: FRED series identifier (e.g., 'GDP')
        :param start_timestamp: first observation date
        :param end_timestamp: last observation date
        :param frequency: data frequency (e.g., 'q', 'sa', 'a')
        :return: relevant FRED series data
        """
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
        SEARCHABLE_ERRORS = [
            "The series does not exist",
            "should be 25 or less alphanumeric",
            "URL can't contain control characters",
        ]
        # Start attempts.
        while attempt <= max_attempts:
            try:
                series = self._client.get_series(
                    id_,
                    **loading_kwargs,
                )
            except Exception as err:
                if "Value of frequency" in str(err):
                    _LOG.error(
                        "Attempt: %s Retrying without frequency parameter...", err
                    )
                    # Remove invalid frequency and retry.
                    loading_kwargs.pop("frequency", None)
                elif "Internal Server Error" in str(err):
                    _LOG.error("Attempt %s: %s Retrying...", attempt, err)
                    attempt += 1
                elif any(sub in str(err) for sub in SEARCHABLE_ERRORS):
                    # Find top 5 closest matches to the invalid query.
                    recs = "No closest matches."
                    matches = self._client.search(id_)
                    if matches is not None:
                        recs = f"Did you mean: {str(list(matches.iloc[0:5, 0]))}"
                    raise ValueError(f"Attempt {attempt}: {err} {recs} ") from err
                elif "Too Many Requests" in str(err):
                    # Retry after exponential backoff.
                    _LOG.error(
                        "Attempt %d: %s Retrying after %ds... ",
                        attempt,
                        err,
                        2**attempt,
                    )
                    time.sleep(2**attempt)
                    continue
                else:
                    raise
                err_msgs[f"Attempt {attempt}"] = str(err)
                attempt += 1
                continue
            df = series.to_frame(name=id_)
            _LOG.info(
                "Downloaded series %s with %d records",
                id_,
                len(df),
            )
            return df
        raise RuntimeError(
            f"Failed to fetch after {max_attempts} attempts. Errors per run {err_msgs}"
        )
