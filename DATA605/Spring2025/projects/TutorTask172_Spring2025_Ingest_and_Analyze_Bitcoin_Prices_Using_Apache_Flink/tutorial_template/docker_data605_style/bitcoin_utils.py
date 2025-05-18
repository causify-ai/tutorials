# --- bitcoin_utils.py ---
import os
import time
import requests
from collections import deque
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

import yfinance as yf
import pandas as pd
from neuralprophet import NeuralProphet
import matplotlib.pyplot as plt

# === General Settings ===
FETCH_INTERVAL = 30  # Seconds between fetches
WINDOW_SIZE = 10     # Number of points in rolling window
EMA_ALPHA = 0.2      # EMA smoothing factor

# === Runtime Environment ===
RUN_ENV = os.getenv("RUN_ENV", "local")

# === InfluxDB Configuration ===
INFLUXDB_URL = os.getenv("INFLUXDB_URL") or (
    "http://influxdb_container:8086" if os.getenv("RUN_ENV") == "docker" else "http://localhost:8086"
)

INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "crypto")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "bitcoin_prices")


class BitcoinPriceSource:
    def __init__(self, interval_sec=FETCH_INTERVAL, window_size=WINDOW_SIZE):
        self.interval = interval_sec
        self.window_size = window_size
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        self.price_window = deque(maxlen=window_size)
        self.ema = None

        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG,
            timeout=30000
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def __iter__(self):
        while True:
            try:
                response = requests.get(self.api_url, params=self.params, timeout=10)
                data = response.json()

                if "bitcoin" in data and "usd" in data["bitcoin"]:
                    price = float(data["bitcoin"]["usd"])
                    change_pct = float(data["bitcoin"].get("usd_24h_change", 0))
                    timestamp = int(time.time() * 1000)
                    current_time = datetime.utcnow()
                    self.price_window.append(price)

                    # Write price point
                    self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG,
                                         record=Point("bitcoin_price").field("price", price).time(current_time))
                    print(f"[{current_time}] Price: ${price:.2f}")

                    # If window is full, compute metrics
                    if len(self.price_window) == self.window_size:
                        ma = sum(self.price_window) / self.window_size
                        variance = sum((x - ma) ** 2 for x in self.price_window) / self.window_size
                        std_dev = variance ** 0.5
                        self.ema = price if self.ema is None else EMA_ALPHA * price + (1 - EMA_ALPHA) * self.ema
                        max_price = max(self.price_window)
                        min_price = min(self.price_window)
                        trend = 1 if self.price_window[-1] > self.price_window[0] else -1
                        cumulative_return = ((self.price_window[-1] - self.price_window[0]) / self.price_window[0]) * 100

                        print(f"-----> MA: ${ma:.2f}, StdDev: {std_dev:.2f}, EMA: ${self.ema:.2f}, "
                              f"Max: ${max_price:.2f}, Min: ${min_price:.2f}")
                        print(f"        Trend: {trend}, Cumulative Return: {cumulative_return:.2f}%, "
                              f"24h Change: {change_pct:.2f}%\n")

                        # Write metrics
                        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG,
                                             record=Point("bitcoin_stats")
                                             .field("moving_avg", ma)
                                             .field("std_dev", std_dev)
                                             .field("ema", self.ema)
                                             .field("max", max_price)
                                             .field("min", min_price)
                                             .field("trend", trend)
                                             .field("cumulative_return", cumulative_return)
                                             .field("percent_change_24h", change_pct)
                                             .time(current_time))

                    yield (timestamp, price)
                else:
                    print("API error: unexpected response ->", data)

            except Exception as e:
                print("Error:", e)

            time.sleep(self.interval)


# === Forecasting Utilities ===

# Fetch historical BTC data from Yahoo Finance
def fetch_historical_data(ticker="BTC-USD", start="2013-01-01"):
    df = yf.download(ticker, start=start, progress=False)
    df = df.reset_index()
    df = df[['Date', 'Close']]
    df.columns = ['ds', 'y']  # Required format for NeuralProphet
    df['ds'] = pd.to_datetime(df['ds'])
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    return df.dropna()

# Train NeuralProphet model on daily data
def train_neural_prophet_model(df):
    model = NeuralProphet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df, freq='D')
    return model

# Generate 1-year forecast using trained model
def make_forecast(model, df, periods=365):
    future = model.make_future_dataframe(df, periods=periods)
    forecast = model.predict(future)
    return forecast

# Plot forecasted BTC prices
def plot_forecast(model, forecast):
    fig = model.plot(forecast, plotting_backend="matplotlib")
    plt.suptitle("Bitcoin Price Forecast (Next 1 Year)")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.show()

# Plot trend and seasonality components
def plot_components(model, forecast):
    fig = model.plot_components(forecast, plotting_backend="matplotlib")
    plt.tight_layout()
    plt.show()
