
"""Script to log real-time Bitcoin price data using utility functions.

1. Uses utility functions from utils.py for modularity
2. CoinGecko API: https://www.coingecko.com/en/api/documentation

Filename: bitcoin_data_logger.py
"""

import logging
import time

from PyMC3_API_utils import get_bitcoin_price, save_to_csv

_LOG = logging.getLogger(__name__)

# Configuration
NUM_ENTRIES = 20
INTERVAL = 10
CSV_FILE = "bitcoin_price_data.csv"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _LOG.info("Starting data logging: %d entries every %d seconds", NUM_ENTRIES, INTERVAL)

    for _ in range(NUM_ENTRIES):
        ts, price = get_bitcoin_price()
        save_to_csv(ts, price, CSV_FILE)
        time.sleep(INTERVAL)
