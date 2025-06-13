"""
Utility functions for Bitcoin data processing with cuDF.
This module contains helper functions for processing Bitcoin price data using cuDF.
"""

import cudf
import numpy as np
from datetime import datetime, timedelta
import time

def load_data(csv_path):
    """
    Load Bitcoin price data from a CSV file into a cuDF DataFrame.
    
    Args:
        csv_path (str): Path to the CSV file containing Bitcoin price data.
        
    Returns:
        cudf.DataFrame: A DataFrame containing the loaded data.
    """
    try:
        df = cudf.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def calculate_sma(df, column="price", windows=[7, 14, 30]):
    """
    Calculate Simple Moving Averages for the specified column.
    
    Args:
        df (cudf.DataFrame): DataFrame containing Bitcoin price data.
        column (str): Column name to calculate SMAs for.
        windows (list): List of window sizes for which to calculate SMAs.
        
    Returns:
        cudf.DataFrame: DataFrame with SMA columns added.
    """
    for window in windows:
        df[f'sma_{window}'] = df[column].rolling(window).mean()
    return df

def calculate_volatility(df, column="price", window=14):
    """
    Calculate price volatility (standard deviation) over a rolling window.
    
    Args:
        df (cudf.DataFrame): DataFrame containing Bitcoin price data.
        column (str): Column name to calculate volatility for.
        window (int): Size of the rolling window.
        
    Returns:
        cudf.DataFrame: DataFrame with volatility column added.
    """
    df[f'volatility_{window}'] = df[column].rolling(window).std()
    return df

def calculate_rsi(df, column="price", window=14):
    """
    Calculate the Relative Strength Index (RSI) for the specified column.
    
    Args:
        df (cudf.DataFrame): DataFrame containing Bitcoin price data.
        column (str): Column name to calculate RSI for.
        window (int): Size of the rolling window.
        
    Returns:
        cudf.DataFrame: DataFrame with RSI column added.
    """
    # Calculate price changes
    delta = df[column].diff()
    
    # Separate gains and losses
    gain = delta.copy()
    loss = delta.copy()
    
    gain = gain.where(gain > 0, 0)
    loss = loss.where(loss < 0, 0).abs()
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    df[f'rsi_{window}'] = rsi
    return df

def fetch_realtime_data(api_client, interval=5, points=30):
    """
    Fetch real-time Bitcoin price data at specified intervals.
    
    Args:
        api_client: API client for fetching Bitcoin price data.
        interval (int): Time interval between data points in seconds.
        points (int): Number of data points to collect.
        
    Returns:
        cudf.DataFrame: DataFrame containing the collected real-time data.
    """
    data = []
    
    print(f"Collecting {points} data points with {interval} second intervals...")
    
    for i in range(points):
        timestamp = datetime.now()
        price = api_client.get_latest_price()
        data.append({"timestamp": timestamp, "price": price})
        
        if i < points - 1:  # Don't sleep after the last data point
            time.sleep(interval)
    
    df = cudf.DataFrame(data)
    return df

def combine_historical_realtime(historical_df, realtime_df):
    """
    Combine historical and real-time data into a single DataFrame.
    
    Args:
        historical_df (cudf.DataFrame): DataFrame containing historical data.
        realtime_df (cudf.DataFrame): DataFrame containing real-time data.
        
    Returns:
        cudf.DataFrame: Combined DataFrame.
    """
    # Ensure timestamp columns are in the same format
    historical_df['timestamp'] = cudf.to_datetime(historical_df['timestamp'])
    realtime_df['timestamp'] = cudf.to_datetime(realtime_df['timestamp'])
    
    # Concatenate the DataFrames
    combined_df = cudf.concat([historical_df, realtime_df], ignore_index=True)
    
    # Sort by timestamp
    combined_df = combined_df.sort_values(by='timestamp')
    
    return combined_df 