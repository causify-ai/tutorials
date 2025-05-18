import requests
import csv
from datetime import datetime
import time
import os

# Wait time between fetches (in seconds)
INTERVAL = 2 * 60 * 60  # 2 hours

# Output file path
DATA_PATH = '../data/bitcoin_live.csv'

def fetch_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            price = response.json()['bitcoin']['usd']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            write_mode = 'a' if os.path.exists(DATA_PATH) else 'w'
            with open(DATA_PATH, write_mode, newline='') as f:
                writer = csv.writer(f)
                if write_mode == 'w':
                    writer.writerow(['timestamp', 'price_usd'])
                writer.writerow([timestamp, price])

            print(f"[{timestamp}] ✅ {price} USD saved.")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

# Run indefinitely
while True:
    fetch_price()
    time.sleep(INTERVAL)
