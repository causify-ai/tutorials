# data/raw_data/bitcoin_yahoo_ohlcv.py
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

RAW_DIR = "data/raw_data"
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_bitcoin_yahoo_ohlcv(start: str = "2014-01-01") -> pd.DataFrame:
    """
    Fetch daily OHLCV for BTC-USD from Yahoo Finance from `start` to today.
    """
    # Download from yfinance
    df = yf.download(
        "BTC-USD",
        start=start,
        end=datetime.utcnow().strftime("%Y-%m-%d"),
        interval="1d",
        progress=False
    )

    # Rename & reset index (treat Close as price)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["open", "high", "low", "price", "volume"]
    df.reset_index(inplace=True)
    df.rename(columns={"Date":"timestamp"}, inplace=True)

    # Save CSV
    out_csv = os.path.join(RAW_DIR, "bitcoin_yahoo_ohlcv_max.csv")
    df.to_csv(out_csv, index=False)
    print(f"Wrote {len(df)} rows → {out_csv}")
    return df

if __name__ == "__main__":
    df = fetch_bitcoin_yahoo_ohlcv(start="2013-01-01")
    print(df.head())