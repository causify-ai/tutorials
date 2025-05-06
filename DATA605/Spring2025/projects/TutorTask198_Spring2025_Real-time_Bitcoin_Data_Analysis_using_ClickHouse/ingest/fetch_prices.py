import time
import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_current_price(retries: int = 3, backoff: int = 10) -> float:
    """
    Fetch the latest Bitcoin price in USD, with simple retry/backoff on 429.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd", "precision": "full"}

    for attempt in range(1, retries + 1):
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()["bitcoin"]["usd"]
        elif resp.status_code == 429:
            # Too many requests → wait and retry
            wait = backoff * attempt
            print(f"429 received, sleeping {wait}s before retry {attempt}/{retries}…")
            time.sleep(wait)
        else:
            # some other error
            resp.raise_for_status()

    # If we get here, we never got a valid price
    raise RuntimeError("Could not fetch current price after retries")


def fetch_historical_prices(days: int = 365, interval: str = "hourly") -> pd.DataFrame:
    """
    Fetch historical daily Bitcoin prices for the past `days`.

    Args:
        days: Number of days to retrieve.

    Returns:
        DataFrame with ['timestamp', 'price'] columns (UTC).
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": interval}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    entries = resp.json().get("prices", [])
    df = pd.DataFrame(entries, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["price"] = df["price"].astype(float)
    return df


def fetch_historical_hourly_prices(
    days: int = 365,
    retries: int = 3,
    backoff_base: int = 5,
    throttle_seconds: float = 1.0,
) -> pd.DataFrame:
    """
    Fetch up to `days` of historical Bitcoin prices at true hourly granularity,
    by querying /market_chart/range in 90-day chunks, with retry/backoff on 429s.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    chunk = timedelta(days=90)
    dfs = []

    while start < end:
        chunk_end = min(start + chunk, end)
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
        params = {
            "vs_currency": "usd",
            "from": int(start.timestamp()),
            "to": int(chunk_end.timestamp()),
        }

        # retry loop for this chunk
        for attempt in range(1, retries + 1):
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                break
            elif resp.status_code == 429:
                wait = backoff_base * attempt
                print(f"[429] waiting {wait}s before retry {attempt}/{retries}…")
                time.sleep(wait)
            else:
                resp.raise_for_status()
        else:
            raise RuntimeError(
                f"Failed to fetch chunk {start} → {chunk_end} after {retries} retries"
            )

        # parse successful response
        prices = resp.json().get("prices", [])
        df_chunk = pd.DataFrame(prices, columns=["timestamp", "price"])
        df_chunk["timestamp"] = pd.to_datetime(df_chunk["timestamp"], unit="ms")
        df_chunk["price"] = df_chunk["price"].astype(float)
        dfs.append(df_chunk)

        # throttle before next chunk
        time.sleep(throttle_seconds)
        start = chunk_end

    # concatenate, dedupe, and index
    df = pd.concat(dfs).drop_duplicates(subset="timestamp").set_index("timestamp")

    # resample hourly, interpolate any gaps
    df = df.resample("h").mean().interpolate()
    df = df.reset_index()
    return df
