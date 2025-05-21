# File: bitcoin_utils.py

import os
import requests
import pandas as pd
from datetime import datetime

# Configuration
API_KEY = os.getenv("COINGECKO_API_KEY", "")
DEFAULT_CSV_PATH = "bitcoin_price_log_from_db.csv"

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()["bitcoin"]["usd"]

def save_to_csv(price, csv_path=DEFAULT_CSV_PATH):
    timestamp = datetime.utcnow()
    df = pd.DataFrame([{"timestamp": timestamp, "price": price}])
    df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
    print(f"[{timestamp}] Saved Bitcoin price to CSV: ${price}")
