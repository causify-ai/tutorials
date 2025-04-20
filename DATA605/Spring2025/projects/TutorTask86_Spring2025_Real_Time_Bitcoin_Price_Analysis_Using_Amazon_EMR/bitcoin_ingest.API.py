import requests
import json
import os
from datetime import datetime
import time

# Constants
API_URL = "https://api.coingecko.com/api/v3/simple/price"
PARAMS = {
    "ids": "bitcoin",
    "vs_currencies": "usd"
}
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "bitcoin_prices.json")

def fetch_bitcoin_price():
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        data = response.json()

        price_usd = data["bitcoin"]["usd"]
        timestamp = datetime.utcnow().isoformat()

        record = {
            "timestamp": timestamp,
            "price_usd": price_usd
        }

        print(f"[{timestamp}] BTC Price: ${price_usd}")
        return record

    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def save_record(record):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Append to file
    with open(LOG_FILE, "a") as f:
        json.dump(record, f)
        f.write("\n")  # Newline-delimited JSON (NDJSON)

def main():
    while True:
        record = fetch_bitcoin_price()
        if record:
            save_record(record)

        # Wait before fetching again
        time.sleep(60)  # Fetch every 60 seconds

if __name__ == "__main__":
    main()
