import requests
import pandas as pd
from datetime import datetime
import time
import os

filename = "/Users/aj/Library/CloudStorage/GoogleDrive-ajayport@umd.edu/My Drive/Bitcoin_Analysis/bitcoin_realtime.csv"

# Initialize CSV with headers if not already present
if not os.path.exists(filename):
    pd.DataFrame(columns=["timestamp", "price_usd"]).to_csv(filename, index=False)

def fetch_bitcoin_data():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raise error if response is bad
        data = response.json()
        price = data.get('bitcoin', {}).get('usd', None)
        
        if price is not None:
            return {
                "timestamp": datetime.utcnow(),
                "price_usd": price
            }
    except Exception as e:
        print(f"[Error] {e}")
    
    return None  # return None on failure

print("⏳ Fetching Bitcoin price every 10 seconds...")

try:
    while True:
        record = fetch_bitcoin_data()
        if record:
            print(f"[{record['timestamp']}] ${record['price_usd']}")
            pd.DataFrame([record]).to_csv(filename, mode='a', header=False, index=False)
        else:
            print("[Skipped] Invalid or missing price. Not recorded.")
        
        time.sleep(10)

except KeyboardInterrupt:
    print("\n⛔ Stopped by user.")
