import logging as log
import os
import time
from typing import Dict, Optional

import gridstatusio
import pandas as pd
import ratelimit

_LOG = log.getLogger(__name__)

# #############################################################################
# GridStatusDataDownloader
# #############################################################################


class GridStatusDataDownloader:
    """
    Download historical data from GridStatus.io.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the GridStatus data downloader with the API key.

        If no API key is passed as a parameter, it is read from the
        GRIDSTATUS_API_KEY environment variable.

        :param api_key: GridStatus API key
        """
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

        Example of timestamp - "2010-01-01 08:00:00+00:00"

        Example of a returned series:

        ```
        interval_start_utc          interval_end_utc            region          market  non_spinning_reserves   regulation_down regulation_mileage_down regulation_mileage_up   regulation_up   spinning_reserves
        2010-01-01 08:00:00+00:00   2010-01-01 09:00:00+00:00   AS_CAISO        DAM     0.0                     0.00            NaN                     NaN                     0.00000         0.00
        2010-01-01 08:00:00+00:00   2010-01-01 09:00:00+00:00   AS_CAISO_EXP    DAM     0.5                     2.25            NaN                     NaN                     10.00089        2.08
        ```

        :param id_: GridStatus dataset identifier (e.g., "caiso_as_prices")
        :param start_timestamp: first observation timestamp
        :param end_timestamp: last observation timestamp (non inclusive)
        :return: relevant GridStatus series data
        """
        # Build request parameters.
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
                    dataset=id_,
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
