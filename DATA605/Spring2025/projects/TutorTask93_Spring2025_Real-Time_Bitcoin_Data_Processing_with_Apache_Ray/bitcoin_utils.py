"""
bitcoin_utils.py

This file contains utility functions and Ray-based components for real-time Bitcoin price ingestion and analysis.

- Notebooks should call these functions and actors instead of embedding logic inline.
- Supports ingestion, transformation, analysis, and filtering of Bitcoin price data.
- Built using Apache Ray for distributed and parallel execution.
"""

import requests
import ray
import time
import pandas as pd
import logging
import yfinance as yf
from datetime import datetime

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Ray Initialization
# -----------------------------------------------------------------------------
ray.shutdown()
ray.init(ignore_reinit_error=True, include_dashboard=False)

# -----------------------------------------------------------------------------
# Function: Fetch Bitcoin Price
# -----------------------------------------------------------------------------
@ray.remote
def fetch_bitcoin_price():
    """
    Fetch the current Bitcoin price in USD using the CoinGecko API.

    :return: (timestamp, price) tuple
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return time.time(), response.json()["bitcoin"]["usd"]
        else:
            return time.time(), None
    except Exception as e:
        logger.error(f"Error fetching price: {e}")
        return time.time(), None

# -----------------------------------------------------------------------------
# Actor: PriceProcessor
# -----------------------------------------------------------------------------
@ray.remote
class PriceProcessor:
    """
    Ray Actor that stores and processes streaming Bitcoin price data.
    """
    def __init__(self):
        self.prices = []

    def add_price(self, timestamp, price):
        if price is not None:
            self.prices.append((timestamp, price))
        return len(self.prices)

    def get_data(self):
        return self.prices

    def get_data_with_readable_time(self):
        return [
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)),
                "price": price
            }
            for ts, price in self.prices
        ]

    def compute_moving_average(self, window=5):
        df = pd.DataFrame(self.prices, columns=["timestamp", "price"])
        if len(df) < window:
            return []
        df["moving_avg"] = df["price"].rolling(window=window).mean()
        return df.to_dict("records")

    def compute_percentage_changes(self):
        if len(self.prices) < 2:
            return []
        pct_changes = []
        for i in range(1, len(self.prices)):
            prev = self.prices[i - 1][1]
            curr = self.prices[i][1]
            change = ((curr - prev) / prev) * 100 if prev != 0 else 0
            pct_changes.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.prices[i][0])),
                "price": curr,
                "percent_change": round(change, 4)
            })
        return pct_changes

    def filter_prices_above(self, threshold):
        return [
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)),
                "price": price
            }
            for ts, price in self.prices if price > threshold
        ]

    def compute_volatility(self, window=5):
        if len(self.prices) < window + 1:
            return []

        returns = []
        for i in range(1, len(self.prices)):
            prev = self.prices[i - 1][1]
            curr = self.prices[i][1]
            ret = ((curr - prev) / prev) if prev != 0 else 0
            returns.append((self.prices[i][0], ret))

        df = pd.DataFrame(returns, columns=["timestamp", "return"])
        df["volatility"] = df["return"].rolling(window=window).std()
        df["timestamp"] = df["timestamp"].apply(lambda ts: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)))
        return df.dropna().to_dict("records")
    
# -----------------------------------------------------------------------------
# Helper Function: Load CSV into Actor
# -----------------------------------------------------------------------------
def load_csv_to_actor(file_path, actor):
    """
    Loads historical CSV data and adds it to the PriceProcessor actor.

    :param file_path: Path to the CSV file
    :param actor: Instance of PriceProcessor (Ray actor)
    """
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for _, row in df.iterrows():
        ts = row["timestamp"].timestamp()
        price = row["price"]
        ray.get(actor.add_price.remote(ts, price))

# -----------------------------------------------------------------------------
# Helper Function: Run Stream Simulation
# -----------------------------------------------------------------------------
def run_price_stream(processor, interval=10, max_fetches=10):
    """
    Simulate a streaming environment by periodically fetching prices.

    :param processor: PriceProcessor Ray actor
    :param interval: Time in seconds between fetches
    :param max_fetches: Total number of prices to fetch
    """
    for _ in range(max_fetches):
        timestamp, price = ray.get(fetch_bitcoin_price.remote())
        logger.info(f"Fetched @ {time.strftime('%H:%M:%S', time.localtime(timestamp))}: ${price}")
        ray.get(processor.add_price.remote(timestamp, price))
        time.sleep(interval)

def fetch_hourly_btc_yfinance(period="7d", interval="1m"):
    print(f"Fetching BTC-USD data for the past {period} at {interval} intervals...")
    btc = yf.download(tickers="BTC-USD", period=period, interval=interval)
    btc.reset_index(inplace=True)
    return btc

