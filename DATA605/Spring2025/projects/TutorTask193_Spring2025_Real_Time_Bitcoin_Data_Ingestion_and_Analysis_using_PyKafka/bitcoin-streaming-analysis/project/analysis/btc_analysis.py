import pandas as pd
from collections import deque

price_window = deque(maxlen=20)

def analyze_data(price_data):
    price_window.append(price_data['price'])
    if len(price_window) >= 5:
        sma = sum(price_window) / len(price_window)
        print(f"SMA: {sma:.2f}, Current: {price_data['price']}")