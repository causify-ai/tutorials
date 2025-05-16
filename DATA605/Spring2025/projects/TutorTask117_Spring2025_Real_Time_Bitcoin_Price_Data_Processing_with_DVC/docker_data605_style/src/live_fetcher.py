# src/live_fetcher.py

import requests

def fetch_price():
    """
    Fetch real-time Bitcoin price in USD from CoinGecko.
    Returns the price as a float.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data["bitcoin"]["usd"]
    except Exception as e:
        print("Error fetching price:", e)
        return None
