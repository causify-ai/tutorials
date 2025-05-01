# bitcoin_utils.py

import requests
import pandas as pd
import logging
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import requests
import pandas as pd
import logging

def fetch_bitcoin_prices(days=7) -> pd.DataFrame:
    """
    Fetch historical Bitcoin price data from CoinGecko API (hourly granularity supported implicitly).

    :param days: Number of days to fetch (2 to 90 for hourly granularity)
    :return: DataFrame with timestamp and price columns
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
        # Do not pass interval here; it's restricted to enterprise
    }

    logging.info(f"Fetching data from {url} with params {params}")
    response = requests.get(url, params=params)

    try:
        data = response.json()
    except ValueError:
        raise Exception("Failed to parse JSON from response.")

    if "prices" not in data:
        logging.error(f"Missing 'prices' key in response: {data}")
        raise KeyError("'prices' key not found in API response.")

    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
    return prices



def plot_bitcoin_prices(df: pd.DataFrame):
    """
    Plot the price of Bitcoin over time.

    :param df: DataFrame containing timestamps and prices
    """
    logger.info("Plotting Bitcoin price data...")
    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["price"])
    plt.title("Bitcoin Price (USD)")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

