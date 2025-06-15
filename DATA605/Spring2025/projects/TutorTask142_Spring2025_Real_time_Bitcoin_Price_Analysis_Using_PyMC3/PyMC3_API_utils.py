
"""Utility functions for Bitcoin price retrieval and logging.

1. CoinGecko API: https://www.coingecko.com/en/api/documentation
2. Lint before commit using flake8, black, isort

Filename: utils.py
"""

import logging
import os
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd
import requests

_LOG = logging.getLogger(__name__)

API_URL = "https://api.coingecko.com/api/v3/simple/price"
PARAMS = {"ids": "bitcoin", "vs_currencies": "usd"}


def get_bitcoin_price() -> Tuple[Optional[str], Optional[float]]:
    """
    Fetch the current Bitcoin price in USD from CoinGecko API.

    :return: Tuple of (timestamp string, price float) or (None, None) on failure
    """
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        data = response.json()
        price = data["bitcoin"]["usd"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return timestamp, price
    except Exception as e:
        _LOG.error("Error while fetching data: %s", e)
        return None, None


def save_to_csv(timestamp: Optional[str], price: Optional[float], csv_file: str) -> None:
    """
    Save timestamp and price data to a CSV file.

    :param timestamp: Timestamp string
    :param price: Bitcoin price in USD
    :param csv_file: Path to the CSV file
    :return: None
    """
    if timestamp is None or price is None:
        return

    row = pd.DataFrame({"timestamp": [timestamp], "price": [price]})

    if os.path.exists(csv_file):
        existing = pd.read_csv(csv_file)
        updated = pd.concat([existing, row], ignore_index=True)
    else:
        updated = row

    updated.to_csv(csv_file, index=False)
    _LOG.info("Logged: %s | Price: %s", timestamp, price)
