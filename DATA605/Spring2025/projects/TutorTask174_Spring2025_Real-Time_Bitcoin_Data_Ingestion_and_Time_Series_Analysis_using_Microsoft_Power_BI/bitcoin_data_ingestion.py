import requests
import time
import csv
from datetime import datetime

output_file = "bitcoin_price_transformed.csv"

def get_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_market_cap": "true"
    }
    response = requests.get(url, params=params)
    data = response.json()["bitcoin"]
    return {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "price_usd": data["usd"],
        "market_cap_usd": data["usd_market_cap"]
    }

# Check if file is empty or doesn't exist, add header
try:
    with open(output_file, 'r') as f:
        file_exists = f.readline().strip() != ""
except FileNotFoundError:
    file_exists = False

if not file_exists:
    with open(output_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "price_usd", "market_cap_usd", "price_change_pct"])
        writer.writeheader()

previous_price = None
while True:
    record = get_bitcoin_data()
    
    if previous_price is None:
        record["price_change_pct"] = 0
    else:
        change = (record["price_usd"] - previous_price) / previous_price
        record["price_change_pct"] = round(change, 5)

    previous_price = record["price_usd"]

    with open(output_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        writer.writerow(record)

    print(f"Appended row: {record}")
    time.sleep(60)  # Run every 60 seconds
