# load_historical_data.py

import os
import pandas as pd
from src.bitcoin_full_pb2 import BitcoinFullData

def load_protobuf_file(file_path):
    """Load and parse all BitcoinFullData records from a binary file."""
    messages = []
    with open(file_path, "rb") as f:
        while True:
            try:
                msg = BitcoinFullData()
                msg.ParseFromString(f.read(msg.ByteSize()))
                messages.append(msg)
            except Exception:
                break
    return messages

def protobufs_to_dataframe(messages):
    """Convert list of BitcoinFullData messages to a DataFrame."""
    rows = []
    for msg in messages:
        rows.append({
            "timestamp": msg.timestamp,
            "id": msg.id,
            "symbol": msg.symbol,
            "name": msg.name,
            "current_price": msg.current_price,
            "market_cap": msg.market_cap,
            "total_volume": msg.total_volume,
            "high_24h": msg.high_24h,
            "low_24h": msg.low_24h,
            "price_change_24h": msg.price_change_24h,
            "market_cap_rank": msg.market_cap_rank,
            "circulating_supply": msg.circulating_supply,
            "ath": msg.ath,
            "atl": msg.atl,
            "source": msg.source,
            "last_updated": msg.last_updated,
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    all_data = []

    for file in os.listdir(data_dir):
        if file.endswith(".bin"):
            path = os.path.join(data_dir, file)
            messages = load_protobuf_file(path)
            df = protobufs_to_dataframe(messages)
            all_data.append(df)

    full_df = pd.concat(all_data, ignore_index=True)
    print(full_df.head())