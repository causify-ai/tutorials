"""
LightGBM_utils.py

Reusable utility functions for real-time Bitcoin price forecasting using LightGBM.
"""

import pandas as pd
import requests
import lightgbm as lgb
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

def fetch_bitcoin_data(days=200):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()["prices"]
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

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

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)
    return rmse, mae, y_test, y_pred

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
