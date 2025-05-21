import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Global list to store fetched data
timestamps = []
prices = []

# CSV path
csv_path = "bitcoin_price_log.csv"

# Your CoinGecko API key (or leave blank for free tier)
API_KEY = os.getenv("COINGECKO_API_KEY", "")

# Fetch Bitcoin price from CoinGecko
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["bitcoin"]["usd"]

# Append to CSV
def append_to_csv(timestamp, price):
    df = pd.DataFrame([{"timestamp": timestamp, "price": price}])
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False, mode='w')
    else:
        df.to_csv(csv_path, index=False, mode='a', header=False)

# Update plot each minute
def update_plot(frame):
    try:
        price = fetch_bitcoin_price()
        timestamp = datetime.utcnow()
        timestamps.append(timestamp)
        prices.append(price)
        append_to_csv(timestamp, price)

        # Clear and redraw plot
        plt.cla()
        plt.plot(timestamps, prices, marker='o', linestyle='-')
        plt.xlabel("Time (UTC)")
        plt.ylabel("Price (USD)")
        plt.title("Live Bitcoin Price (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Print to terminal
        print(f"[{timestamp}] Fetched: ${price}")

    except Exception as e:
        print(f"[{datetime.utcnow()}] ⚠️ Error fetching price: {e}")

# Set up live plot
fig = plt.figure(figsize=(10, 5))
ani = FuncAnimation(fig, update_plot, interval=60000, cache_frame_data=False)
plt.show()
