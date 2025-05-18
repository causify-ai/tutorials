"""
LightGBM_utils.py

Utility functions for real-time Bitcoin price analysis and forecasting using LightGBM.

This module provides reusable functionality for:

- Fetching live and historical Bitcoin prices from public APIs (CoinGecko)
- Preprocessing time series data: creating lag features, rolling statistics, and time-based attributes
- Training and evaluating a LightGBM regression model for price prediction
- Visualizing model predictions, error distributions, and feature importances
- Supporting real-time forecasting pipelines with feature generation and trend analysis

"""


import pandas as pd
import requests
import lightgbm as lgb
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import requests
from datetime import datetime
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA

from scipy.stats import linregress



#def fetch_bitcoin_data(days=200):
#    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
#    response = requests.get(url)
#    response.raise_for_status()
#    data = response.json()["prices"]
#    df = pd.DataFrame(data, columns=["timestamp", "price"])
#    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
#    return df

import requests
import pandas as pd
from datetime import datetime

#------------------------------------------------------------------------------------------------------------------------------------------------# #DATA INGESTION
#------------------------------------------------------------------------------------------------------------------------------------------------
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

# def get_historical_bitcoin_data(days=365):
#     """
#     Fetch historical Bitcoin price data for the past N days using CoinGecko API.
#     Returns a DataFrame with 'date' and 'price' columns.
#     """
#     url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
#     response = requests.get(url)
#     response.raise_for_status()
#     prices = response.json()["prices"]

#     df = pd.DataFrame(prices, columns=["timestamp", "price"])
#     df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
#     return df[["date", "price"]]

def get_historical_bitcoin_data(days=365):
    """
    Fetch historical Bitcoin price data (hourly if <90 days, daily otherwise).
    Returns a DataFrame with timestamp and price columns.
    """
    interval = "hourly" if days <= 90 else "daily"
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    url += f"?vs_currency=usd&days={days}&interval={interval}"

    response = requests.get(url)
    response.raise_for_status()
    prices = response.json()["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df[["timestamp", "price"]]



def get_combined_bitcoin_data(days=5, include_latest=True):
    """
    Combine historical and optional live price data into a single DataFrame.
    """
    df_hist = get_historical_bitcoin_data(days=days)
    
    if include_latest:
        live = fetch_bitcoin_price()
        df_latest = process_price_data(live)
        df_combined = pd.concat([df_hist, df_latest], ignore_index=True)
    else:
        df_combined = df_hist

    return df_combined
#------------------------------------------------------------------------------------------------------------------------------------------------
# Time Series Analysis
#------------------------------------------------------------------------------------------------------------------------------------------------


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
#----------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------

def create_features(df):
    df = df.copy()
    df["minute"] = df["timestamp"].dt.minute
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["lag_1"] = df["price"].shift(1)
    df["lag_2"] = df["price"].shift(2)
    df["rolling_mean_3"] = df["price"].rolling(3).mean()
    df["rolling_std_3"] = df["price"].rolling(3).std()
    df = df.dropna()
    return df

def train_lightgbm(df):
    features = ["minute", "hour", "dayofweek", "lag_1", "lag_2", "rolling_mean_3", "rolling_std_3"]
    X = df[features]
    y = df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = lgb.LGBMRegressor()
    model.fit(X_train, y_train)
    return model, X_test, y_test

# def evaluate_model(model, X_test, y_test):
#     y_pred = model.predict(X_test)
#     rmse = mean_squared_error(y_test, y_pred, squared=False)
#     mae = mean_absolute_error(y_test, y_pred)
#     return rmse, mae, y_test, y_pred


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)
    return rmse, mae, y_test, y_pred

def evaluate_realtime_prediction(y_pred, y_actual):
    """
    Evaluate real-time prediction by comparing predicted and actual price.
    Returns RMSE and MAE for a single data point.
    """
    rmse = mean_squared_error([y_actual], [y_pred], squared=False)
    mae = mean_absolute_error([y_actual], [y_pred])
    return rmse, mae


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


def plot_predictions(y_test, y_pred):
    plt.figure(figsize=(10, 5))
    plt.plot(y_test.index, y_test, label="Actual")
    plt.plot(y_test.index, y_pred, label="Predicted", linestyle="--")
    plt.title("Actual vs Predicted Bitcoin Prices")
    plt.xlabel("Time Index")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    plt.show()



def plot_error_distribution(y_test, y_pred):
    errors = y_test - y_pred
    plt.figure(figsize=(10, 5))
    sns.histplot(errors, kde=True, bins=30)
    plt.title("Prediction Error Distribution")
    plt.xlabel("Error")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

def plot_feature_importance(model, feature_names):
    """
    Plots the importance of each feature used by the LightGBM model.
    """
    importance = model.feature_importance()
    indices = np.argsort(importance)[::-1]

    plt.figure(figsize=(12, 6))
    sns.barplot(x=importance[indices], y=np.array(feature_names)[indices])
    plt.title("Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Features")
    plt.tight_layout()
    plt.show()

import requests
from datetime import datetime

def get_current_btc_price():
    """
    Fetch the current Bitcoin price in USD using CoinGecko API.
    Returns (timestamp, price) tuple.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        price = data["bitcoin"]["usd"]
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return timestamp, price
    except Exception as e:
        print("Error fetching price:", e)
        return None, None

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def plot_daily_price_with_moving_average(df, window=7):
    df = df.copy()
    df["ma"] = df["price"].rolling(window=window).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["price"], label="Daily BTC Price", color="blue", linewidth=1.5)
    plt.plot(df["timestamp"], df["ma"], label=f"{window}-Day Moving Average", color="orange", linewidth=2)
    plt.title(f"Bitcoin Daily Price with {window}-Day Moving Average")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

