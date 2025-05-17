# bitcoin_utils.py


import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------------
# Data Ingestion (from data_ingestion.py)
# ---------------------------
# src/data_ingestion.py

import os
import pandas as pd
from datetime import datetime
from src.live_fetcher import fetch_price

def record_price(filepath="data/bitcoin_prices.csv"):
    """
    Fetch current price and append it to a CSV with timestamp.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    price = fetch_price()
    if price is None:
        print("Price not available.")
        return
    timestamp = datetime.utcnow().isoformat()
    df = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price"])

    if os.path.exists(filepath):
        df.to_csv(filepath, mode='a', header=False, index=False)
    else:
        df.to_csv(filepath, index=False)

# ---------------------------
# Real-Time Fetch Loop (from live_fetcher.py)
# ---------------------------
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


# ---------------------------
# Preprocessing + Plot (from preprocess_eda.py)
# ---------------------------
# src/preprocess_eda.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def preprocess(filepath="data/bitcoin_prices.csv", outpath="data/cleaned_bitcoin.csv"):
    """
    Load BTC price data, compute diff and rolling average, save cleaned CSV.
    """
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['price_diff'] = df['price'].diff()
    df['rolling_avg'] = df['price'].rolling(window=5).mean()

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    df.to_csv(outpath, index=False)
    return df

def plot_data(df, output_path="Output/bitcoin_price_plot.png"):
    """
    Save a time series line chart from the cleaned data.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.plot(x='timestamp', y='price', title="Bitcoin Price Over Time", figsize=(10, 5))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
