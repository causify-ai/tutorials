import os
import time
import requests
import pandas as pd
from datetime import datetime

# === Configuration ===
API_KEY = os.getenv("COINGECKO_API_KEY", "")
CSV_PATH = "bitcoin_price_log_from_db.csv"
FETCH_INTERVAL = 60  # seconds

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()["bitcoin"]["usd"]

def save_to_csv(price):
    timestamp = datetime.utcnow()
    df = pd.DataFrame([{"timestamp": timestamp, "price": price}])
    df.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)
    print(f"[{timestamp}] Saved Bitcoin price to CSV: ${price}")

if __name__ == "__main__":
    while True:
        try:
            price = fetch_bitcoin_price()
            save_to_csv(price)
        except Exception as e:
            print(f"[{datetime.utcnow()}] Error occurred: {e}")
        time.sleep(FETCH_INTERVAL)
