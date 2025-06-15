"""
bitcoin_petl_utils.py

Utility functions to fetch and process Bitcoin price data via Petl.
Keeps the tutorials notebook clean by handling all API & ETL logic here.
"""
import pandas as pd
import time
import requests
import petl as etl
import os

# API endpoint for CoinGecko simple price
CG_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin"
    "&vs_currencies=usd"
    "&include_last_updated_at=true"
)
def fetch_btc_price_table() -> etl.Table:
    """
    Hit CoinGecko and grab the latest BTC price in USD.
    Returns a one-row Petl table with:
      - timestamp: UNIX seconds
      - price_usd: float
    """
    resp = requests.get(CG_URL)
    resp.raise_for_status()
    info = resp.json().get("bitcoin", {})
    row = {
        "timestamp": info.get("last_updated_at"),
        "price_usd": info.get("usd")
    }
    # Here we wrap it up in a Petl table for easy downstream ETL
    return etl.fromdicts([row])

def filter_recent(table: etl.Table, lookback_min: int = 15) -> etl.Table:
    """
    Take a Petl table with a 'timestamp' column, convert it to int,
    and keep only rows within the last `lookback_min` minutes.
    """
    cutoff = int(time.time()) - lookback_min * 60
    tbl_int = etl.convert(table, 'timestamp', int)
    return etl.select(tbl_int, "{timestamp} >= %d" % cutoff)

def expand_demo_rows(single_row: etl.Table, n: int = 5, dt: int = 60) -> etl.Table:
    """
    For tutorial demos: clone a single-row table into `n` rows,
    each offset by `dt` seconds, then sort by timestamp ascending.
    """
    original = next(iter(etl.dicts(single_row)))
    clones = []
    for i in range(n):
        clone = dict(original)
        clone['timestamp'] -= i * dt
        clones.append(clone)
    multi = etl.fromdicts(clones).sort('timestamp')
    return multi

def fetch_historical_range(from_ts: int, to_ts: int) -> etl.Table:
    """
    Fetch historical BTC price data between two UNIX timestamps
    using CoinGecko's market_chart/range endpoint.
    Returns a Petl table with columns:
      - timestamp (int seconds)
      - price_usd (float)
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {
        "vs_currency": "usd",
        "from": from_ts,
        "to":   to_ts,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    # 'prices' is a list of [ms, price]
    rows = [
        {"timestamp": int(ms/1000), "price_usd": price}
        for ms, price in resp.json().get("prices", [])
    ]
    return etl.fromdicts(rows)

def compute_indicators(table: etl.Table, window: int = 3) -> etl.Table:
    """
    Given a Petl table with 'timestamp' and 'price_usd',
    compute moving average and volatility over a rolling window.
    Appends two new columns: 'MA_{window}' and 'VOL_{window}'.
    """
    # Convert to pandas behind the scenes for rolling convenience:
    df = etl.todataframe(table)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    df[f"MA_{window}"]  = df["price_usd"].rolling(window).mean()
    df[f"VOL_{window}"] = df["price_usd"].rolling(window).std()
    # Back to Petl
    df = df.reset_index()
    df['timestamp'] = df['timestamp'].view(int) // 10**9
    return etl.fromdataframe(df)

def alert_on_threshold(table: etl.Table, threshold: float) -> etl.Table:
    """
    Filter rows where price_usd crosses above a given threshold.
    Useful for generating alerts when BTC price spikes above a level.
    """
    tbl = etl.convert(table, 'price_usd', float)
    return etl.select(tbl, "{price_usd} >= %f" % threshold)
def init_csv(path: str):
    """Delete any existing CSV and write a fresh header-only file."""
    if os.path.exists(path):
        os.remove(path)
    fetch_btc_price_table().tocsv(path, write_header=True)

def append_price(path: str):
    """Fetch the latest BTC price and append it to the CSV."""
    etl.appendcsv(fetch_btc_price_table(), path)

def load_dataframe(path: str) -> pd.DataFrame:
    """Load CSV into a pandas DataFrame, parse timestamps, and set index."""
    df = pd.read_csv(path, header=0)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("timestamp", inplace=True)
    return df

def add_indicators(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """Compute rolling moving average and volatility."""
    df = df.copy()
    df[f"MA_{window}"]  = df["price_usd"].rolling(window).mean()
    df[f"VOL_{window}"] = df["price_usd"].rolling(window).std()
    return df