import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Global lists to store data for plotting
timestamps = []
prices = []

# API key (optional)
API_KEY = os.getenv("COINGECKO_API_KEY", "")

# Fetch Bitcoin price from CoinGecko
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()["bitcoin"]["usd"]

# Update plot every minute
def update_plot(frame):
    try:
        price = fetch_bitcoin_price()
        timestamp = datetime.utcnow()
        timestamps.append(timestamp)
        prices.append(price)

        # Clear and update plot
        plt.cla()
        plt.plot(timestamps, prices, marker='o', linestyle='-')
        plt.xlabel("Time (UTC)")
        plt.ylabel("Price (USD)")
        plt.title("Live Bitcoin Price (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        print(f"[{timestamp}] Fetched: ${price}")

    except Exception as e:
        print(f"[{datetime.utcnow()}] Error fetching price: {e}")

# Set up the plot
fig = plt.figure(figsize=(10, 5))
ani = FuncAnimation(fig, update_plot, interval=60000, cache_frame_data=False)
plt.show()
