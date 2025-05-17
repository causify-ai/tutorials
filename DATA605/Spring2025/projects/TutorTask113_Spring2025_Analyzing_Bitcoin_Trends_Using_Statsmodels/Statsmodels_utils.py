""" 
statsmodels_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
""" 

import time
import pandas as pd
import requests
import matplotlib.pyplot as plt
import logging
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Function: Fetch 1-day historical BTC data (1-min intervals)
# -----------------------------------------------------------------------------

def fetch_historical_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}
    response = requests.get(url, params=params)
    try:
        data = response.json()
        prices = data["prices"]
    except KeyError:
        logger.error("Unexpected API response format.")
        logger.error(response.text)
        raise
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df = df.resample("1min").mean().dropna()
    return df

# -----------------------------------------------------------------------------
# Function: Simulate real-time streaming
# -----------------------------------------------------------------------------

def simulate_realtime(df, minutes=3):
    logger.info(f"Simulating {minutes} minutes of real-time price updates...")
    for _ in range(minutes):
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        price = response.json()['bitcoin']['usd']
        now = pd.Timestamp.utcnow()
        df.loc[now] = price
        logger.info(f"[{now}] Appended price: ${price}")
        time.sleep(60)
    return df

# -----------------------------------------------------------------------------
# Function: Plot raw BTC time series
# -----------------------------------------------------------------------------

def plot_time_series(df, title="Real-Time BTC Price (USD)"):
    """
    Plot the raw BTC price time series.

    :param df: DataFrame with a datetime index and 'price' column
    :param title: Title for the plot
    """
    df['price'].plot(figsize=(12, 4), title=title)
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Function: Fit ARIMA and forecast
# -----------------------------------------------------------------------------

def run_arima_analysis(df):
    df = df.resample("1min").mean().ffill()
    model = ARIMA(df['price'], order=(2, 1, 2))
    results = model.fit()
    forecast = results.forecast(steps=30)
    return results, forecast

# -----------------------------------------------------------------------------
# Function: Plot forecast
# -----------------------------------------------------------------------------

def plot_forecast(df, forecast):
    plt.figure(figsize=(14, 6))
    plt.plot(df.index[-120:], df['price'].tail(120), label="Actual Price")
    forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(minutes=1), periods=30, freq="1min")
    plt.plot(forecast_index, forecast, label="Forecast (Next 30 mins)", color="orange")
    plt.xlabel("Time (UTC)")
    plt.ylabel("BTC Price (USD)")
    plt.title("Bitcoin Price Forecast using ARIMA (UTC)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Function: Save actual and forecast data to CSV
# -----------------------------------------------------------------------------

def save_to_csv(df, forecast):
    df.to_csv("btc_full_data.csv", index=True)
    forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(minutes=1), periods=30, freq="1min")
    forecast_df = pd.DataFrame({"timestamp": forecast_index, "forecast_price": forecast.values})
    forecast_df.set_index("timestamp", inplace=True)
    forecast_df.to_csv("btc_price_forecast.csv", index=True)
    logger.info("Data saved to 'btc_full_data.csv' and 'btc_price_forecast.csv'.")

# -----------------------------------------------------------------------------
# Function: Plot ACF and PACF
# -----------------------------------------------------------------------------

def plot_acf_pacf(df, lags=40):
    plt.figure(figsize=(10, 4))
    plot_acf(df['price'], lags=lags)
    plt.title("Autocorrelation Function (ACF)")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 4))
    plot_pacf(df['price'], lags=lags, method='ywm')
    plt.title("Partial Autocorrelation Function (PACF)")
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Function: Fetch and save BTC data for any time range (1, 30, 365 days)
# -----------------------------------------------------------------------------

def fetch_and_process_data(days: int, filename: str, title: str):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    response = requests.get(url, params=params)
    data = response.json()
    if "prices" not in data:
        logger.error(f"Unexpected response for {days} days.")
        logger.error(response.text)
        return None
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    if days == 1:
        df = df.resample("1min").mean()
    elif days == 30:
        df = df.resample("1H").mean()
    else:
        df = df.resample("1D").mean()
    df.dropna(inplace=True)
    df.to_csv(filename)
    logger.info(f"Saved data for {title} to {filename}")
    plt.figure(figsize=(12, 4))
    plt.plot(df.index, df["price"], label="Price (USD)")
    plt.title(f"Bitcoin Price - {title}")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return df
