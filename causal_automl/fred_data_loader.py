import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from fredapi import Fred

_LOG = logging.getLogger(__name__)


# #############################################################################
# FredDataLoader
# #############################################################################


class FredDataLoader:
    """
    Load time series data from FRED.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Initialize loader with API key.

        :param api_key: fred api key or none to read from environment
            variable
        """
        key = api_key or os.getenv("FRED_API_KEY")
        if not key:
            raise ValueError("fred api key is required")

        self._client = Fred(api_key=key)

    def load_series(
        self,
        id_: str,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Load a series and return it as DataFrame.

        :param id_: fred series identifier (e.g., 'GDP')
        :param start_timestamp: first observation date
        :param end_timestamp: last observation date
        :return: data in a compatible format
        """
        # Fetch data using optional date filters.
        series = self._client.get_series(
            id_,
            observation_start=start_timestamp,
            observation_end=end_timestamp,
        )
        # Represent data in the required format.
        df = series.to_frame(name=id_)
        _LOG.info(
            "downloaded series %s with %d records",
            id_,
            len(df),
        )

        return df
