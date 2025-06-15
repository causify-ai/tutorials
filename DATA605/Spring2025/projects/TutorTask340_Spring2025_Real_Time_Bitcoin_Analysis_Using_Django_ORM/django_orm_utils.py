import requests
from datetime import datetime
from bitcoin_app.models import BitcoinPrice
from django.utils import timezone
import numpy as np
from scipy.signal import find_peaks

def get_current_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 429:
        print("Rate limit exceeded — skipping fetch.")
        return None  # gracefully handle failure
    response.raise_for_status()
    return response.json()["bitcoin"]["usd"]


def store_price_in_db(price):
    BitcoinPrice.objects.create(timestamp=timezone.now(), price_usd=price)

def fetch_and_store():
    price = get_current_bitcoin_price()
    if price is not None:
        store_price_in_db(price)
    return price

def get_last_n_prices(n=50):
    return BitcoinPrice.objects.order_by('-timestamp')[:n][::-1]

def compute_average(prices):
    return round(np.mean(prices), 2)

def compute_volatility(prices):
    return round(np.std(prices), 2)

def detect_peaks(prices):
    peaks, _ = find_peaks(prices)
    return peaks.tolist()

