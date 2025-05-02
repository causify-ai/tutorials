# bitcoin_utils.py

import os
import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data["bitcoin"]["usd"]
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def record_price(filename="data/bitcoin_prices.csv"):
    os.makedirs("data", exist_ok=True)
    price = fetch_bitcoin_price()
    if price is None:
        return
    timestamp = datetime.datetime.utcnow().isoformat()
    df = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price"])
    
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

def plot_prices(input_file="data/bitcoin_prices.csv", output_file="Output/plot.png"):
    os.makedirs("Output", exist_ok=True)
    df = pd.read_csv(input_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.plot(x='timestamp', y='price', title='Bitcoin Price Over Time', figsize=(10, 4))
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
