import time
import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_current_price(retries: int = 5, backoff: int = 10) -> float:
    """
    Fetch the latest Bitcoin price in USD from CoinGecko, with retry/backoff support.

    Args:
        retries: Number of retry attempts on failure.
        backoff: Base wait time (in seconds) for exponential backoff.

    Returns:
        The latest price as a float.

    Raises:
        RuntimeError if all retries fail.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd", "precision": "full"}

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=10)
            print(f"Attempt {attempt} → Status: {resp.status_code}")

            if resp.status_code == 200:
                price = resp.json()["bitcoin"]["usd"]
                print(f"✅ Fetched current price: ${price}")
                return price

            elif resp.status_code == 429:
                wait = backoff * attempt
                print(
                    f"⏳ 429 Too Many Requests — sleeping {wait}s before retry {attempt}/{retries}"
                )
                time.sleep(wait)
            elif resp.status_code == 500:
                print(f"⚠️ Server error on attempt {attempt}: {resp.text}")
                resp.raise_for_status()
            else:
                print(f"⚠️ Unexpected status {resp.status_code}: {resp.text}")
                resp.raise_for_status()

        except requests.RequestException as e:
            print(f"⚠️ Request error on attempt {attempt}: {e}")
            time.sleep(backoff * attempt)

    raise RuntimeError("❌ Could not fetch current price after retries")


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
