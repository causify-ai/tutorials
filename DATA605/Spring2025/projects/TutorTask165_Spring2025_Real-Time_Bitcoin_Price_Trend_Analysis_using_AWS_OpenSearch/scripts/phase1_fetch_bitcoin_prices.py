from pycoingecko import CoinGeckoAPI
import json
import time
from datetime import datetime
import os

# Initialize CoinGecko API
cg = CoinGeckoAPI()

# Output file
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bitcoin_prices.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print("Starting live price fetch. Press Ctrl+C to stop.")

try:
    while True:
        # Fetch current price
        price_data = cg.get_price(ids='bitcoin', vs_currencies='usd')
        price = price_data['bitcoin']['usd']

        # Current timestamp in ISO format
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

        # Create record
        record = {
            "timestamp": timestamp,
            "price": price
        }

        # Append to file
        with open(output_path, 'a') as f:
            f.write(json.dumps(record) + '\n')

        print(f"[{timestamp}]  BTC Price: ${price}")

        # Wait 45 seconds
        time.sleep(45)

except KeyboardInterrupt:
    print("\nStopped live fetching by user.")
