# data/raw_data/bitcoin_last_year_coingecko.py

import os
import requests
import pandas as pd
from datetime import datetime

RAW_DIR = "data/raw_data"
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_bitcoin_last_year():
    """
    Fetch daily price, market cap, and volume for the last 365 days
    from CoinGecko’s free API.
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": 365}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    df_price = pd.DataFrame(data["prices"], columns=["ts", "price"])
    df_cap   = pd.DataFrame(data["market_caps"], columns=["ts", "market_cap"])
    df_vol   = pd.DataFrame(data["total_volumes"], columns=["ts", "total_volume"])

    df = (
        df_price
        .merge(df_cap, on="ts")
        .merge(df_vol, on="ts")
    )
    df["timestamp"] = pd.to_datetime(df["ts"], unit="ms")
    df = df[["timestamp", "price", "market_cap", "total_volume"]]
    df.sort_values("timestamp", inplace=True)
    df.to_csv(os.path.join(RAW_DIR, "bitcoin_1y_coingecko.csv"), index=False)
    print(f"Wrote {len(df)} rows → bitcoin_1y_coingecko.csv")
    return df

if __name__ == "__main__":
    fetch_bitcoin_last_year()