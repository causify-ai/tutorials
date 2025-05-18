# rasa_utils.py

"""
BitcoinAPI wrapper around CoinGecko endpoints.
Dependencies: requests, pandas
"""

import requests
import pandas as pd

class BitcoinAPI:
    """
    A thin wrapper around the CoinGecko Bitcoin price endpoints.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, vs_currency: str = "usd"):
        """
        :param vs_currency: fiat currency to compare against (e.g. 'usd', 'eur')
        """
        self.vs_currency = vs_currency

    def get_current_price(self) -> float:
        """
        Fetches the current price of Bitcoin.
        :return: latest price as float
        """
        resp = requests.get(
            f"{self.BASE_URL}/simple/price",
            params={"ids": "bitcoin", "vs_currencies": self.vs_currency},
        )
        resp.raise_for_status()
        return resp.json()["bitcoin"][self.vs_currency]

    def get_historical_data(
        self,
        days: int = 30,
        interval: str = "daily"
    ) -> pd.DataFrame:
        """
        Fetches Bitcoin price history for the past N days.
        :param days: how many days back to fetch (max 90)
        :param interval: 'hourly' or 'daily'
        :return: DataFrame with ['timestamp','price']
        """
        resp = requests.get(
            f"{self.BASE_URL}/coins/bitcoin/market_chart",
            params={
                "vs_currency": self.vs_currency,
                "days": days,
                "interval": interval,
            },
        )
        resp.raise_for_status()
        prices = resp.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp_ms", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
        return df[["timestamp", "price"]]

    def summarize_trends(self, df: pd.DataFrame) -> dict:
        """
        Computes high, low, and mean over a DataFrame of prices.
        :param df: DataFrame from get_historical_data
        :return: dict with keys 'high','low','mean'
        """
        return {
            "high": df["price"].max(),
            "low": df["price"].min(),
            "mean": df["price"].mean(),
        }

if __name__ == "__main__":
    # Quick self-test
    api = BitcoinAPI()
    print("Current BTC price:", api.get_current_price())
    df = api.get_historical_data(days=7)
    print(df.head())