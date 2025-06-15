"""
Fetches and stores real-time Bitcoin price data using CoinGecko API.

1. CoinGecko API Reference: https://www.coingecko.com/en/api/documentation
2. pandas for timestamping and saving structured data.
3. Script duration: 3 hours, data fetched every 10 seconds.

Refer to: dataprep.connector.API.md for pipeline and ingestion design.
Coding style guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import time
from typing import Optional, Dict, List

import pandas as pd
import requests

from API_utils import (
    setup_logging,
    handle_api_error,
    save_data_to_csv,
    validate_price_response
)

_LOG = setup_logging(__name__)


class BitcoinDataCollector:
    """
    Collects real-time Bitcoin prices at fixed intervals using the CoinGecko API.
    """

    def __init__(self, interval_seconds: int = 10, duration_seconds: int = 10800):
        """
        Initialize collection parameters.

        :param interval_seconds: Time between API calls in seconds.
        :param duration_seconds: Total duration to collect data for, in seconds.
        """
        self.interval = interval_seconds
        self.duration = duration_seconds
        self.iterations = duration_seconds // interval_seconds
        self.data: List[Dict] = []

    def fetch_price(self) -> Optional[Dict[str, object]]:
        """
        Fetch current Bitcoin price from CoinGecko API.

        :return: Dictionary with timestamp and price or None on failure.
        """
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            price = validate_price_response(response.json())
            if price is not None:
                return {
                    'timestamp': pd.Timestamp.now(),
                    'price_usd': price
                }
            else:
                _LOG.warning("Unexpected response structure: %s", response.json())
                return None
        except Exception as e:
            handle_api_error(e, _LOG)
            return None

    def collect(self) -> None:
        """
        Run the data collection loop.
        """
        _LOG.info("Starting data collection for %.1f minutes...", self.duration / 60)
        for _ in range(self.iterations):
            entry = self.fetch_price()
            if entry:
                self.data.append(entry)
                _LOG.info("[%s] Price: $%s", entry['timestamp'], entry['price_usd'])
            time.sleep(self.interval)

    def save_to_csv(self, filepath: str = "bitcoin_real_time_data.csv") -> None:
        """
        Save the collected data to a CSV file.

        :param filepath: Path to output CSV file.
        """
        save_data_to_csv(self.data, filepath)
        _LOG.info("Data collection completed and saved to '%s'.", filepath)


if __name__ == "__main__":
    collector = BitcoinDataCollector()
    collector.collect()
    collector.save_to_csv()
