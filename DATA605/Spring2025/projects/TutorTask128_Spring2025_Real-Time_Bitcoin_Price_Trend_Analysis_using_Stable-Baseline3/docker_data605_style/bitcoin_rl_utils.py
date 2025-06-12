import requests
import pandas as pd

def fetch_bitcoin_data(vs_currency="usd", days=3):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "vs_currency": vs_currency,
        "days": days
        # Removed 'interval'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
        return prices
    else:
        print("Response content:", response.text)
        raise Exception(f"API Error: {response.status_code}")
