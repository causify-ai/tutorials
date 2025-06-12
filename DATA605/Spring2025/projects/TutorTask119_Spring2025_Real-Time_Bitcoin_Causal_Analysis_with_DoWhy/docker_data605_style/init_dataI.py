import os
import pandas as pd
import requests

# Setup
os.makedirs("data", exist_ok=True)
filepath = "data/bitcoin_prices.csv"

# Fetch past 30 days of hourly price data
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {
    "vs_currency": "usd",
    "days": "30",  # Past 30 days
    "interval": "hourly"
}
response = requests.get(url, params=params)
data = response.json()

# Convert to DataFrame
prices = data["prices"]  # [ [timestamp, price], ... ]
df = pd.DataFrame(prices, columns=["timestamp", "price"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.to_csv(filepath, index=False)
print(f" Saved past 30 days data to: {filepath}")
