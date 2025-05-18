import requests
import pandas as pd

def fetch_bitcoin_data(vs_currency="usd", days=3):
    """
    Fetch historical Bitcoin price data for the past N days using CoinGecko.

    Args:
        vs_currency (str): Target currency (default: "usd")
        days (int): Number of past days to fetch

    Returns:
        pd.DataFrame: timestamped Bitcoin prices
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"vs_currency": vs_currency, "days": days}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
        return prices
    except Exception as e:
        print("Failed to fetch historical data:", e)
        raise


def fetch_latest_price():
    """
    Fetch the latest Bitcoin price (in USD) using CoinGecko.

    Returns:
        float: current Bitcoin price
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()["bitcoin"]["usd"]
    except Exception as e:
        print("Failed to fetch latest price:", e)
        raise
