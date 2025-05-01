# data/raw_data/bitcoin_features.py

import os
import requests
import pandas as pd
from datetime import datetime

RAW_DIR = "data/raw_data"
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_bitcoin_features(days: int = 365) -> pd.DataFrame:
    """
    Fetch Bitcoin OHLC + price + market cap + 24h volume for the past `days` days.
    Returns a DataFrame with columns:
      timestamp, open, high, low, close, price, market_cap, total_volume
    """
    coin_id = "bitcoin"
    vs_currency = "usd"

    # 1) Historical chart data (price, market cap, 24h volume)
    url_mc = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params_mc = {"vs_currency": vs_currency, "days": days}
    resp_mc = requests.get(url_mc, params=params_mc)
    resp_mc.raise_for_status()
    mc = resp_mc.json()
    # prices, market_caps, total_volumes are lists of [timestamp_ms, value]
    df_price = pd.DataFrame(mc["prices"], columns=["ts", "price"])
    df_cap   = pd.DataFrame(mc["market_caps"], columns=["ts", "market_cap"])
    df_vol   = pd.DataFrame(mc["total_volumes"], columns=["ts", "total_volume"])

    # 2) OHLC data
    url_ohlc = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params_ohlc = {"vs_currency": vs_currency, "days": days}
    resp_ohlc = requests.get(url_ohlc, params=params_ohlc)
    resp_ohlc.raise_for_status()
    ohlc = resp_ohlc.json()
    # each entry: [timestamp_ms, open, high, low, close]
    df_ohlc = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])

    # 3) Merge on timestamp (ms)
    df = (
        df_ohlc
        .merge(df_price, on="ts", how="left")
        .merge(df_cap,   on="ts", how="left")
        .merge(df_vol,   on="ts", how="left")
    )

    # 4) Convert to datetime and clean up
    df["timestamp"] = pd.to_datetime(df["ts"], unit="ms")
    df = df[["timestamp", "open", "high", "low", "close", "price", "market_cap", "total_volume"]]
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 5) Save to CSV with descriptive filename
    out_csv = os.path.join(RAW_DIR, f"bitcoin_features_{days}d.csv")
    df.to_csv(out_csv, index=False)

    print(f"Wrote {len(df)} records ➜ {out_csv}")
    return df

if __name__ == "__main__":
    # Example: pull last 365 days
    df = fetch_bitcoin_features(days=365)
    print(df.head())