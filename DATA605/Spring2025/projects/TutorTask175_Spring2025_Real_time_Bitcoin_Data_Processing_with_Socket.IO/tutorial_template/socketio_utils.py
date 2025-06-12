# socketio_utils.py

import time
import random
import requests
import numpy as np

# ----------------------------
# 1. Real BTC Price Fetcher
# ----------------------------

def fetch_btc_price():
    url = "https://api.coincap.io/v2/assets/bitcoin"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            price = float(data['priceUsd'])
            timestamp = time.time()
            return {'timestamp': timestamp, 'price': price}
        elif response.status_code == 429:
            print("[ERROR 429] Rate limit hit. Sleeping for 60 seconds...")
            time.sleep(60)
        else:
            print(f"[ERROR] HTTP {response.status_code}")
    except Exception as e:
        print("[EXCEPTION] Request failed:", e)
    return None

# ----------------------------
# 2. Moving Average Function
# ----------------------------

def compute_sma(prices, window=5):
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])

# ----------------------------
# 3. Fake BTC Price Stream
# ----------------------------

def simulate_fake_btc_stream(n=10, interval=2):
    prices = []
    current_price = 27500.0  # Starting price
    for i in range(n):
        change = random.uniform(-50, 50)
        current_price += change
        prices.append(current_price)
        sma = compute_sma(prices)
        print(f"[{i+1}] SIM BTC Price: ${current_price:.2f}, SMA: {sma:.2f}" if sma else f"[{i+1}] SIM BTC Price: ${current_price:.2f}")
        time.sleep(interval)

# ----------------------------
# 4. (Optional) Real BTC Stream
# ----------------------------

def simulate_btc_stream(n=10, interval=6):
    prices = []
    for i in range(n):
        data = fetch_btc_price()
        if data:
            prices.append(data['price'])
            sma = compute_sma(prices)
            print(f"[{i+1}] BTC Price: ${data['price']:.2f}, SMA: {sma:.2f}" if sma else f"[{i+1}] BTC Price: ${data['price']:.2f}")
        time.sleep(interval)

# ----------------------------
# 5. Run standalone
# ----------------------------

if __name__ == "__main__":
    print("Running simulated BTC price stream...")
    simulate_fake_btc_stream(n=10, interval=1)
