# src/data_ingestion.py

import os
import pandas as pd
from datetime import datetime
from src.live_fetcher import fetch_price

def record_price(filepath="data/bitcoin_prices.csv"):
    """
    Fetch current price and append it to a CSV with timestamp.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    price = fetch_price()
    if price is None:
        print("Price not available.")
        return
    timestamp = datetime.utcnow().isoformat()
    df = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price"])

    if os.path.exists(filepath):
        df.to_csv(filepath, mode='a', header=False, index=False)
    else:
        df.to_csv(filepath, index=False)
