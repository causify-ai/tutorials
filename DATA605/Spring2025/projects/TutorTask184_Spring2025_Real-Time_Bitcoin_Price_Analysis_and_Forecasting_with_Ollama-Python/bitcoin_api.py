import requests
from datetime import datetime

def fetch_price_from_coingecko():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        price = data['bitcoin']['usd']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Bitcoin Price: ${price}")
        return price
    except Exception as e:
        print("[ERROR]", e)
        return None

# Temporary test
if __name__ == "__main__":
    fetch_price_from_coingecko()
