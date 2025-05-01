# data/raw_data_ingest.py

import os
import json
import requests
import pandas as pd
from datetime import datetime

RAW_DIR = "data/raw_data"
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_bitcoin_history(days: int = 3650) -> dict:
    """
    Fetch & save historical Bitcoin prices for the past `days` days.
    Returns metadata including file paths, record count, and date range.
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": days}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()["prices"]  # list of [ms_timestamp, price]

    # Build DataFrame
    df = pd.DataFrame(data, columns=["timestamp_ms", "price_usd"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df = df[["timestamp", "price_usd"]]

    # File naming
    csv_path = os.path.join(RAW_DIR, f"bitcoin_history_{days}d.csv")
    meta_path = os.path.join(RAW_DIR, f"bitcoin_history_{days}d.metadata.json")

    # Save CSV
    df.to_csv(csv_path, index=False)

    # Build & save metadata
    metadata = {
        "source": url,
        "params": params,
        "output_csv": csv_path,
        "records": len(df),
        "start_date": df["timestamp"].min().isoformat(),
        "end_date":   df["timestamp"].max().isoformat(),
        "fetched_at": datetime.utcnow().isoformat()
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def fetch_snapshot(date_str: str = "30-12-2020") -> dict:
    """
    Fetch & save a single-day Bitcoin snapshot (DD-MM-YYYY).
    Returns metadata including file paths and key metrics.
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/history"
    params = {"date": date_str, "localization": "false"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    market_data = resp.json().get("market_data", {})

    # Normalize date for filename
    dt = datetime.strptime(date_str, "%d-%m-%Y")
    filename_date = dt.strftime("%Y%m%d")

    json_path = os.path.join(RAW_DIR, f"bitcoin_snapshot_{filename_date}.json")
    meta_path = os.path.join(RAW_DIR, f"bitcoin_snapshot_{filename_date}.metadata.json")

    # Save full snapshot JSON
    with open(json_path, "w") as f:
        json.dump(market_data, f, indent=2)

    # Extract key metadata
    metadata = {
        "source": url,
        "params": params,
        "output_json": json_path,
        "current_price_usd": market_data.get("current_price", {}).get("usd"),
        "market_cap_usd":    market_data.get("market_cap", {}).get("usd"),
        "total_volume_usd":  market_data.get("total_volume", {}).get("usd"),
        "fetched_at":        datetime.utcnow().isoformat()
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    # Example usage:
    hist_meta = fetch_bitcoin_history(days=365)
    print("History metadata:", hist_meta)

    snap_meta = fetch_snapshot("01-01-2021")
    print("Snapshot metadata:", snap_meta)