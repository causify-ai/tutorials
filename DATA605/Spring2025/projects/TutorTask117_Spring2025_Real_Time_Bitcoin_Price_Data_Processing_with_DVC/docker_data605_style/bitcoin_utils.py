import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------------
# 1. Fetch Current BTC Price
# ---------------------------
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
# 2. Record Price with Timestamp
# ---------------------------
def record_price(filepath="data/bitcoin_prices.csv"):
    """
    Fetch current price and append it to a CSV with UTC timestamp.
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
# 3. Loop to Fetch for N Seconds
# ---------------------------
def record_live_prices(duration_seconds=120, interval_seconds=10, output_file="data/bitcoin_prices.csv"):
    """
    Repeatedly record BTC price every interval for total duration.
    """
    iterations = duration_seconds // interval_seconds
    print(f"Recording Bitcoin prices every {interval_seconds} seconds for {duration_seconds} seconds...\n")
    for i in range(iterations):
        record_price(output_file)
        print(f"✔️ Recorded price {i+1}/{iterations}")
        time.sleep(interval_seconds)
    print("\n✅ Finished recording.")

# ---------------------------
# 4. Preprocess + Save Cleaned CSV
# ---------------------------
def preprocess(filepath="data/bitcoin_prices.csv", outpath="data/cleaned_bitcoin.csv"):
    """
    Load BTC price data, clean timestamps, compute price diff and rolling avg.
    Save cleaned version to CSV.
    """
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    df = df.sort_values(by='timestamp')
    df['price_diff'] = df['price'].diff()
    df['rolling_avg'] = df['price'].rolling(window=5).mean()

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    df.to_csv(outpath, index=False)
    return df

# ---------------------------
# 5. Plot Line Chart of Price
# ---------------------------
def plot_data(df, output_path="Output/bitcoin_price_plot.png"):
    """
    Create a line chart of Bitcoin prices over time.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['price'], label='Price (USD)', linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Bitcoin Price')
    plt.title('Bitcoin Price Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"✅ Plot saved to {output_path}")
