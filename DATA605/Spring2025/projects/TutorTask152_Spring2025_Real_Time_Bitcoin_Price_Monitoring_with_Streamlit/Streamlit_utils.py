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
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands


def get_current_price(coin='bitcoin'):
    """
    Fetches the current price of a specified cryptocurrency using the CoinGecko API.
    
    Parameters:
        coin (str): The name of the cryptocurrency (default: 'bitcoin').
    
    Returns:
        float: The current price of the coin in USD.
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data[coin]['usd']


def get_historical_data(coin='bitcoin', days=30):
    """
    Fetches historical daily price data for a specified cryptocurrency from CoinGecko API.
    
    Parameters:
        coin (str): The name of the cryptocurrency (default: 'bitcoin').
        days (int): Number of past days to fetch data for (default: 30 days).
    
    Returns:
        pd.DataFrame: DataFrame containing daily average prices with 'date' and 'price' columns.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.drop('timestamp', axis=1)
    df.set_index('date', inplace=True)
    df_daily = df.resample('D').mean().reset_index()
    return df_daily


def calculate_moving_average(df, window=7):
    """
    Calculates the moving average of the price over a specified window.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with 'price' column.
        window (int): The number of days over which to compute the moving average (default: 7).
    
    Returns:
        pd.DataFrame: DataFrame with an added 'moving_average' column.
    """
    df_processed = df.copy()
    df_processed['moving_average'] = df_processed['price'].rolling(window=window, min_periods=1).mean()
    return df_processed


def calculate_technical_indicators(df):
    """
    Computes multiple technical indicators (RSI, MACD, Bollinger Bands) for the input price data.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with 'price' column.
    
    Returns:
        pd.DataFrame: DataFrame with added columns for RSI, MACD, MACD signal, 
                      Bollinger Bands upper and lower bounds.
    """
    df_ta = df.copy()
    rsi = RSIIndicator(df_ta['price'], window=14)
    df_ta['RSI'] = rsi.rsi()
    macd = MACD(df_ta['price'])
    df_ta['MACD'] = macd.macd()
    df_ta['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(df_ta['price'], window=20, window_dev=2)
    df_ta['BB_upper'] = bb.bollinger_hband()
    df_ta['BB_lower'] = bb.bollinger_lband()
    return df_ta


def detect_anomalies(df, threshold=3):
    """
    Detects anomalies in price movements based on Z-score thresholding.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with 'price' column.
        threshold (float): Z-score value above which a point is considered an anomaly (default: 3).
    
    Returns:
        pd.DataFrame: DataFrame with added columns for 'price_diff', 'z_score', and 'anomaly' flag.
    """
    df_anom = df.copy()
    df_anom['price_diff'] = df_anom['price'].diff()
    df_anom['z_score'] = (df_anom['price_diff'] - df_anom['price_diff'].mean()) / df_anom['price_diff'].std()
    df_anom['anomaly'] = abs(df_anom['z_score']) > threshold
    return df_anom