"""
A clean Bitcoin ETL + analysis API using Bonobo and CoinGecko.

References:
- CoinGecko API documentation: https://www.coingecko.com/en/api/documentation
- Bonobo ETL framework: https://www.bonobo-project.org/
- Pandas & Matplotlib for analysis and plotting

This module defines an API layer for fetching, transforming, saving, and analyzing
Bitcoin price data from CoinGecko using a Bonobo-style pipeline.

Usage:
    from bitcoin_API import BitcoinPipeline
    pipeline = BitcoinPipeline()
    data = pipeline.fetch_data()
    cleaned = pipeline.transform_data(data)
    pipeline.save_data(cleaned)
    pipeline.analyze_data()

Conforms to https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import logging
import time
import requests
import csv
from typing import Optional, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt

_LOG = logging.getLogger(__name__)


class BitcoinPipeline:
    """
    Provides methods to fetch, transform, store, and analyze Bitcoin data.
    """

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches the current Bitcoin price in USD from the CoinGecko API, with retries.

        :return: JSON response dictionary or None if failed.
        """
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        for attempt in range(3):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                _LOG.error("Error fetching data (attempt %d): %s", attempt + 1, e)
                time.sleep(5)
        return None

    def transform_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parses and formats the raw API response into a flat dictionary.

        :param data: Raw API JSON data
        :return: Dict with timestamp and price or None
        """
        if data and "bitcoin" in data:
            return {
                "timestamp": time.time(),
                "bitcoin_usd": data["bitcoin"].get("usd")
            }
        return None

    def save_data(self, row: Optional[Dict[str, Any]], filepath: str = "bitcoin_data.csv") -> None:
        """
        Appends a dictionary to a CSV file with header if missing.

        :param row: Transformed data row to append
        :param filepath: Output file path
        :return: None
        """
        if row is None:
            _LOG.warning("Attempted to save empty row. Skipping.")
            return

        with open(filepath, "a", newline="") as file:
            fieldnames = ["timestamp", "bitcoin_usd"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(row)

    def analyze_data(self, filepath: str = "bitcoin_data.csv") -> None:
        """
        Reads the data from CSV and performs a 10-period moving average plot.

        :param filepath: CSV file with Bitcoin data
        :return: None
        """
        try:
            df = pd.read_csv(filepath)

            if 'timestamp' not in df.columns:
                _LOG.error("No timestamp column in CSV. Skipping analysis.")
                return

            df.dropna(subset=["timestamp", "bitcoin_usd"], inplace=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            df['moving_average'] = df['bitcoin_usd'].rolling(window=10).mean()

            plt.figure(figsize=(10, 6))
            plt.plot(df.index, df['bitcoin_usd'], label='Bitcoin Price (USD)', color='blue')
            plt.plot(df.index, df['moving_average'], label='10-period Moving Avg', linestyle='--', color='red')
            plt.title('Bitcoin Price and Moving Average')
            plt.xlabel('Time')
            plt.ylabel('Price (USD)')
            plt.legend()
            plt.tight_layout()
            plt.savefig("btc_plot.png")
            plt.close()
            _LOG.info("Time series analysis complete. Plot saved as btc_plot.png.")

        except Exception as e:
            _LOG.error("Error during time series analysis: %s", e)