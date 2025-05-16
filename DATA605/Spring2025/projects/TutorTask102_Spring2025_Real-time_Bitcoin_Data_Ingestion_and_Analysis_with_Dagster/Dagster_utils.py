"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import requests
import pandas as pd
from datetime import datetime

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

def get_historical_bitcoin_data(days=180):
    """
    Fetch historical Bitcoin price data for the past 180 days using CoinGecko API.
    Returns a DataFrame with 'date' and 'price' columns.
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    prices = response.json()["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
    return df[["date", "price"]]


def calculate_moving_average(df, window_days=7):
    """
    Calculates the moving average of Bitcoin prices over a specified number of days.
    
    Assumes data is sampled every 5 minutes (i.e., 288 data points per day).

    Parameters:
        df (pd.DataFrame): DataFrame containing a 'price' column.
        window_days (int): Number of days for moving average. Default is 7.

    Returns:
        pd.DataFrame: DataFrame with added 'moving_average' column.
    """
    df_processed = df.copy()

    # Calculate window size in number of rows (5-minute intervals)
    window_size = window_days * 288  # 288 points/day

    # Compute moving average
    df_processed['moving_average'] = df_processed['price'].rolling(window=window_size, min_periods=1).mean()

    return df_processed

def detect_trend(df):
    """
    Detect a basic trend using linear regression (slope sign).
    Returns 'upward', 'downward', or 'flat'.
    """
    from scipy.stats import linregress
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
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with 'price' column.
        threshold (float): Z-score value above which a point is considered an anomaly (default: 2.5). 
    
    Returns:
        pd.DataFrame: DataFrame with added columns for 'price_diff', 'z_score', and 'anomaly' flag.
    """ 
    df = df.copy()
    mean = df["price"].mean()
    std = df["price"].std()
    df["z_score"] = (df["price"] - mean) / std
    df["anomaly"] = df["z_score"].abs() > threshold
    return df

def plot_price_with_moving_average(df):
    """
    Plot Bitcoin price with its moving average.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["price"], label="Price")
    plt.plot(df["date"], df["moving_average"], label="5-day MA", linestyle="--")  # ✅ Fixed here
    plt.title("Bitcoin Price & Moving Average")
    plt.xlabel("Date")
    plt.ylabel("USD")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()