import requests
import pandas as pd
from datetime import datetime
import os
import time

# Number of data points to collect and time interval in seconds
NUM_ENTRIES = 20
INTERVAL = 10

# Output CSV file
CSV_FILE = "bitcoin_price_data.csv"

# CoinGecko API configuration
API_URL = "https://api.coingecko.com/api/v3/simple/price"
PARAMS = {
    "ids": "bitcoin",
    "vs_currencies": "usd"
}

# Fetch current Bitcoin price and timestamp
def get_bitcoin_price():
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        data = response.json()
        price = data["bitcoin"]["usd"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return timestamp, price
    except Exception as e:
        print("Error while fetching data:", e)
        return None, None

# Save the timestamp and price to CSV
def save_to_csv(timestamp, price):
    if timestamp is None or price is None:
        return

    row = pd.DataFrame({
        "timestamp": [timestamp],
        "price": [price]
    })

    if os.path.exists(CSV_FILE):
        existing = pd.read_csv(CSV_FILE)
        updated = pd.concat([existing, row], ignore_index=True)
    else:
        updated = row

    updated.to_csv(CSV_FILE, index=False)
    print(f"Logged: {timestamp} | Price: {price}")

# Main loop to run data logging
if __name__ == "__main__":
    print(f"Starting data logging: {NUM_ENTRIES} entries every {INTERVAL} seconds\n")

    for i in range(NUM_ENTRIES):
        print(f"Collecting entry {i + 1} of {NUM_ENTRIES}")
        timestamp, price = get_bitcoin_price()
        save_to_csv(timestamp, price)
        time.sleep(INTERVAL)

    print("\nData logging complete.")
