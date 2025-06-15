import requests
import pandas as pd
import yaml
import os
from datetime import datetime
from dotenv import load_dotenv

def load_config(path="config/config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

def fetch_market_chart_data(config, override_days=None):
    
    load_dotenv() 
    api_key = os.getenv("COINGECKO_API_KEY")

    url = config["api"]["base_url"]
    params = {
        "vs_currency": config["api"]["vs_currency"],
        "days": override_days or config["api"]["days"],
        # "interval": override_interval or config["api"]["interval"]
    }

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    market_caps = pd.DataFrame(data["market_caps"], columns=["timestamp", "market_cap"])
    volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])

    df = prices.merge(market_caps, on="timestamp").merge(volumes, on="timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def save_market_data(df, folder="data"):
    os.makedirs(folder, exist_ok=True)
    filename = f"btc_market_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(folder, filename)
    df.to_csv(path, index=False)
    print(f"Saved market data to {path}")
    return path


def load_realtime_btc_data(days: int = 30, currency: str = "usd") -> pd.DataFrame:
    """
    Fetch real-time Bitcoin market chart data using CoinGecko API.

    Args:
        days (int): Number of past days to retrieve (default 30)
        currency (str): Quoted currency (default 'usd')

    Returns:
        pd.DataFrame: DataFrame with timestamp, price, market cap, volume
    """
    config = {
        "api": {
            "base_url": "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
            "vs_currency": currency,
            "days": days
        }
    }
    return fetch_market_chart_data(config)