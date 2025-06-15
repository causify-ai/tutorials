# src/load_historical_data.py

import os
import requests
import datetime
from src.bitcoin_full_pb2 import BitcoinFullData

# ----------- Utility Functions -----------

def fetch_hourly_historical_data():
    """Fetch past 30 days of hourly Bitcoin market data from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "30", "interval": "hourly"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def dict_to_protobuf(ts, price, market_cap, volume):
    """Convert a single data point to a BitcoinFullData protobuf object."""
    return BitcoinFullData(
        timestamp=int(ts // 1000),
        current_price=price,
        market_cap=market_cap,
        total_volume=volume,
        source="coingecko",
    )

def save_to_length_delimited_file(messages, output_path):
    """Save protobuf messages using length-delimited encoding."""
    with open(output_path, "wb") as f:
        for msg in messages:
            serialized = msg.SerializeToString()
            size = len(serialized)
            f.write(size.to_bytes(4, byteorder="little"))
            f.write(serialized)

# ----------- Main Script -----------

if __name__ == "__main__":
    print("🌐 Fetching 30 days of hourly Bitcoin data from CoinGecko...")
    data = fetch_hourly_historical_data()

    timestamps = data["prices"]
    market_caps = {ts: mc for ts, mc in data["market_caps"]}
    volumes = {ts: vol for ts, vol in data["total_volumes"]}

    messages = []
    for ts, price in timestamps:
        mc = market_caps.get(ts, 0.0)
        vol = volumes.get(ts, 0.0)
        proto = dict_to_protobuf(ts, price, mc, vol)
        messages.append(proto)

    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "bitcoin_historical_hourly.pb")

    save_to_length_delimited_file(messages, output_path)
    print(f"✅ Saved {len(messages)} hourly records to {output_path}")