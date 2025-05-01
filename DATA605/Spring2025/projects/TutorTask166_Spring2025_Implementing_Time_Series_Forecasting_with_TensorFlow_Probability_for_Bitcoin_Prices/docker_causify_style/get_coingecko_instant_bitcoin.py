#!/usr/bin/env python3
"""
get_coingecko_instant_bitcoin.py

Fetches consolidated OHLC summary and market metrics for Bitcoin every minute,
using CoinGecko's public API, with rate limiting, rotating user agents,
retries, and appends new rows to a single CSV under data/raw_data/instant_data/.
"""
import os
import time
import logging
import random
import requests
import pandas as pd
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
data_dir = "data/raw_data/instant_data"
os.makedirs(data_dir, exist_ok=True)
csv_path = os.path.join(data_dir, "bitcoin_instant.csv")

API_BASE = "https://api.coingecko.com/api/v3"
MARKETCHART = "/coins/bitcoin/market_chart"
SIMPLE_PRICE = "/simple/price"
INTERVAL = 60  # seconds between fetches

# User agents pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/113.0.0.0",
]

# Setup session with retries
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount("https://", HTTPAdapter(max_retries=retry))
session.mount("http://", HTTPAdapter(max_retries=retry))

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS), "Accept": "application/json"}


def fetch_prices_series(days=1):
    """Fetch list of [ms_timestamp, price] for the past `days` days."""
    url = API_BASE + MARKETCHART
    params = {"vs_currency": "usd", "days": days}
    resp = session.get(url, params=params, headers=get_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json().get("prices", [])


def fetch_market_metrics():
    """Fetch current price, 24h high/low, market cap, total volume via simple/price."""
    url = API_BASE + SIMPLE_PRICE
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_high_low": "true"
    }
    resp = session.get(url, params=params, headers=get_headers(), timeout=10)
    resp.raise_for_status()
    data = resp.json().get("bitcoin", {})
    return {
        "price": data.get("usd"),
        "market_cap": data.get("usd_market_cap"),
        "total_volume": data.get("usd_24h_vol"),
        "high_24h": data.get("usd_24h_high"),
        "low_24h": data.get("usd_24h_low")
    }


def summarize_ohlc(series):
    """Compute open, high, low, close from price series list."""
    df = pd.DataFrame(series, columns=["ts", "price"]).dropna()
    if df.empty:
        return None
    df["timestamp"] = pd.to_datetime(df["ts"], unit="ms")
    open_p = df.iloc[0]["price"]
    close_p = df.iloc[-1]["price"]
    return {"open": open_p, "high": df["price"].max(), "low": df["price"].min(), "close": close_p}


def append_row(row: dict):
    """Append a single-row dict to CSV, writing header if needed."""
    df = pd.DataFrame([row])
    write_header = not os.path.exists(csv_path)
    df.to_csv(csv_path, mode="a", header=write_header, index=False)
    logger.info(f"Appended row for {row['timestamp']}")


def main():
    logger.info("Starting instant fetch loop (CTRL+C to stop)")
    try:
        while True:
            try:
                prices = fetch_prices_series(days=1)
                ohlc = summarize_ohlc(prices)
                metrics = fetch_market_metrics()
                if ohlc and metrics:
                    row = {"timestamp": datetime.utcnow().isoformat()}
                    row.update(ohlc)
                    row.update(metrics)
                    append_row(row)
                else:
                    logger.warning("No data to append this cycle")
            except Exception as e:
                logger.error(f"Error fetching/appending: {e}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logger.info("Fetch loop terminated by user")

if __name__ == "__main__":
    main()
