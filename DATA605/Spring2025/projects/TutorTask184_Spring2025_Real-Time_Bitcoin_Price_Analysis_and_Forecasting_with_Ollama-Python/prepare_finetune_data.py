import time
import requests
import pandas as pd

BASE_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"

def fetch_prices(start_ts: int, end_ts: int) -> pd.Series:
    """
    Fetch & resample Bitcoin price at 5-min intervals.
    On HTTP errors (e.g. 429), return an empty series.
    """
    try:
        r = requests.get(BASE_URL, params={
            "vs_currency": "usd",
            "from": start_ts,
            "to":   end_ts
        }, timeout=10)
        r.raise_for_status()
        data = r.json().get("prices")
        if data is None:
            raise ValueError(f"no ‘prices’ in response: {r.text[:200]}")
    except Exception as e:
        print(f"[ERROR] fetch_prices({start_ts},{end_ts}): {e}")
        # return an empty series so downstream code can handle it
        return pd.Series(dtype=float)

    df = pd.DataFrame(data, columns=["timestamp_ms", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    series = df.set_index("timestamp")["price"]
    return series.resample("300S").ffill()
