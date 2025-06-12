import time
import requests
import pandas as pd

BASE_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"

def fetch_prices(start_ts: int, end_ts: int) -> pd.Series:
    """
    Fetch & resample Bitcoin price from `start_ts` to `end_ts` at 5-min intervals.
    """
    r = requests.get(BASE_URL, params={
        "vs_currency": "usd",
        "from": start_ts,
        "to": end_ts
    })
    r.raise_for_status()
    data = r.json()["prices"]  # [[ms, price], …]

    df = pd.DataFrame(data, columns=["timestamp_ms", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    series = df.set_index("timestamp")["price"]
    return series.resample("300S").ffill()
