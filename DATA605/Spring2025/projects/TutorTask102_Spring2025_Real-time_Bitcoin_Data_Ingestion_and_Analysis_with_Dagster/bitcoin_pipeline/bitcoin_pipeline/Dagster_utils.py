"""
Dagster_utils.py

Utility functions for Bitcoin data ingestion and time series analysis.

This file contains reusable logic for:
- Fetching live and historical Bitcoin prices
- Saving to CSV
- Calculating moving averages and detecting trends
- Detecting anomalies using Z-score
- Forecasting future prices with ARIMA
"""

import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from scipy.stats import linregress

# ----------------------------
# Data Ingestion & Processing
# ----------------------------

def fetch_bitcoin_price(api_url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"):
    """
    Fetch the current Bitcoin price in USD using the CoinGecko API.
    Returns a dictionary with a timestamp and the current price.
    """
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    return {
        "timestamp": datetime.now(),
        "price": data["bitcoin"]["usd"]
    }

def process_price_data(data):
    """
    Convert raw price data (dict) into a one-row Pandas DataFrame.
    """
    return pd.DataFrame([data])

def save_to_csv(df, filepath="bitcoin_prices.csv"):
    """
    Append the DataFrame row to a CSV file.
    Creates the file with headers if it doesn't exist.
    """
    write_header = not pd.io.common.file_exists(filepath)
    df.to_csv(filepath, mode="a", header=write_header, index=False)

def get_historical_bitcoin_data(days=365):
    """
    Fetch historical Bitcoin price data for the past N days using CoinGecko API.
    Returns a DataFrame with 'date' and 'price' columns.
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    prices = response.json()["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
    return df[["date", "price"]]

# ----------------------------
# Time Series Analysis
# ----------------------------

def calculate_moving_average(df, window_days=7):
    """
    Calculates the moving average of Bitcoin prices over a specified number of days.
    Assumes data is sampled every 5 minutes (i.e., 288 data points per day).
    """
    df_processed = df.copy()
    window_size = window_days * 288  # 288 points/day
    df_processed['moving_average'] = df_processed['price'].rolling(window=window_size, min_periods=1).mean()
    return df_processed

def detect_trend(df):
    """
    Detect a basic trend using linear regression (slope sign).
    Returns 'upward', 'downward', or 'flat'.
    """
    df = df.copy().reset_index(drop=True)
    if len(df) < 2:
        return "not enough data"
    
    x = range(len(df))
    y = df["price"]
    slope, _, _, _, _ = linregress(x, y)

    if slope > 0:
        return "upward"
    elif slope < 0:
        return "downward"
    else:
        return "flat"

def detect_anomalies_zscore(df, threshold=2.5):
    """
    Detects anomalies in price movements based on Z-score thresholding.
    Returns a DataFrame with added 'z_score' and 'anomaly' columns.
    """
    df = df.copy()
    mean = df["price"].mean()
    std = df["price"].std()
    df["z_score"] = (df["price"] - mean) / std
    df["anomaly"] = df["z_score"].abs() > threshold
    return df

# ----------------------------
# ARIMA Forecasting
# ----------------------------

def fit_arima_model(df, order=(5, 1, 0), forecast_steps=30):
    """
    Fit an ARIMA model and forecast future Bitcoin prices.

    Parameters:
        df (pd.DataFrame): DataFrame with 'date' and 'price'
        order (tuple): ARIMA (p,d,q) order
        forecast_steps (int): Number of future steps to predict

    Returns:
        pd.DataFrame: Combined original and forecasted prices
    """
    df = df.copy()

    # Convert 'date' to datetime and set as index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    #  Drop duplicate index values
    df = df[~df.index.duplicated(keep='first')]

    # Reindex to daily frequency and interpolate missing values
    full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df = df.reindex(full_index)
    df['price'] = df['price'].interpolate(method='time')
    df.index.name = 'date'

    # Fit ARIMA model
    model = ARIMA(df['price'], order=order)
    model_fit = model.fit()

    # Forecast future values
    forecast = model_fit.forecast(steps=forecast_steps)
    last_valid_date = df['price'].last_valid_index()
    forecast_index = pd.date_range(start=last_valid_date + pd.Timedelta(days=1), periods=forecast_steps)

    forecast_df = pd.DataFrame({'price': forecast}, index=forecast_index)

    # Combine historical and forecasted data
    combined_df = pd.concat([df, forecast_df])
    return combined_df



def plot_arima_forecast(df, forecast_steps=30):
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    observed = df.iloc[:-forecast_steps]
    forecasted = df.iloc[-forecast_steps:]

    plt.figure(figsize=(12, 6))
    plt.plot(observed.index, observed["price"], label="Observed", color="blue", linewidth=1.5)

    # Add visible markers to forecast line
    plt.plot(forecasted.index, forecasted["price"], label="Forecast", color="red", linestyle="--", linewidth=2, marker='o', markersize=4)

    #  Optional visual aid
    plt.axvline(x=forecasted.index[0], color='gray', linestyle=':', label='Forecast Start')

    plt.title("Bitcoin Price Forecast (ARIMA)")
    plt.xlabel("Date")
    plt.ylabel("USD")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# ----------------------------
# Plotting
# ----------------------------

def plot_price_with_moving_average(df):
    """
    Plot Bitcoin price with its moving average.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["price"], label="Price")
    if "moving_average" in df.columns:
        plt.plot(df["date"], df["moving_average"], label="Moving Average", linestyle="--")
    plt.title("Bitcoin Price & Moving Average")
    plt.xlabel("Date")
    plt.ylabel("USD")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
