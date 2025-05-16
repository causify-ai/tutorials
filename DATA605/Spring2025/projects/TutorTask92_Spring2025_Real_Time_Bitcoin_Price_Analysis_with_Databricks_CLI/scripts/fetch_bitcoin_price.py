import requests
from datetime import datetime
import json
import os
from config.settings import COINGECKO_PRICE_URL

def fetch_price():
    url = COINGECKO_PRICE_URL
    try:
        res = requests.get(url)
        data = res.json()

        if 'bitcoin' in data and 'usd' in data['bitcoin']:
            price = data['bitcoin']['usd']
            time_now = datetime.utcnow().isoformat()

            record = {
                "timestamp": time_now,
                "price": price
            }

            os.makedirs("data", exist_ok=True)
            with open("data/bitcoin_price.json", "a") as f:
                f.write(json.dumps(record) + "\n")

            print(f"[{time_now}] Bitcoin price: ${price}")
        else:
            print(" Unexpected API response:", data)

    except Exception as e:
        print("Something went wrong while fetching data:", e)

if __name__ == "__main__":
    fetch_price()
