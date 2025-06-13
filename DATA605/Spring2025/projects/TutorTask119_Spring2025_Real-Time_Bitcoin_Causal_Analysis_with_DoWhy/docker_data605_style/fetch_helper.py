import threading
import time
import pandas as pd
import os
import requests
from datetime import datetime

def get_current_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params)
        return response.json()["bitcoin"]["usd"]
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def append_price():
    filepath = "data/bitcoin_prices.csv"
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(filepath):
        df_init = pd.DataFrame(columns=["timestamp", "price"])
        df_init.to_csv(filepath, index=False)

    price = get_current_price()
    if price:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        df = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price"])
        df.to_csv(filepath, mode='a', index=False, header=False)
        print(f"[{timestamp}] Price appended: ${price}")

def start_background_fetch(interval_seconds=60):
    def fetch_loop():
        print("🚀 Background fetcher started...")
        while True:
            append_price()
            time.sleep(interval_seconds)

    thread = threading.Thread(target=fetch_loop, daemon=True)
    thread.start()
