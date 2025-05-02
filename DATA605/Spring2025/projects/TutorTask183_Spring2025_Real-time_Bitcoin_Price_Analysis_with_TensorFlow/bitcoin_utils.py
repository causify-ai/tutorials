"""
bitcoin_utils.py

Utility functions for handling Bitcoin historical price data.

This file contains helper functions to:
- Load and clean CSV datasets.
- Update dataset with latest data from CoinGecko.
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------

import pandas as pd
import logging
import requests

# --------------------------------------------------------------------
# Logging Setup
# --------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# Data Loading & Cleaning
# --------------------------------------------------------------------

def load_and_clean_csv(file_path: str):
    """
    Load and clean the historical Bitcoin dataset from CSV.

    :param file_path: Path to the CSV file (e.g., 'data/btc-usd-max.csv')
    :return: Cleaned DataFrame with datetime index and numeric columns
    """
    logger.info(f"Loading dataset from {file_path}")

    # Load CSV into DataFrame
    df = pd.read_csv(file_path)

    # Convert 'snapped_at' column to datetime
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], utc=True)

    # Sort by timestamp to ensure chronological order
    df = df.sort_values('snapped_at')

    # Set datetime as index (good practice for time series)
    df.set_index('snapped_at', inplace=True)

    # Ensure columns are numeric
    for col in ['price', 'market_cap', 'total_volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where price is missing (critical target)
    df = df.dropna(subset=['price'])

    # Fill missing market_cap and total_volume if needed
    df['market_cap'] = df['market_cap'].fillna(method='ffill')
    df['total_volume'] = df['total_volume'].fillna(method='ffill')

    # Drop duplicate timestamps (if any)
    df = df[~df.index.duplicated(keep='last')]

    # Log shape and column names
    logger.info(f"Dataset loaded: {df.shape[0]} rows; columns: {list(df.columns)}")

    return df

# --------------------------------------------------------------------
# Update Dataset with Latest Data
# --------------------------------------------------------------------

def update_dataset_with_latest(csv_path: str):
    """
    Fetch the latest Bitcoin data point from CoinGecko and append it
    to the existing dataset if it's a new timestamp.

    :param csv_path: Path to the existing CSV file (e.g., 'data/btc-usd-max.csv')
    """
    logger.info(f"Loading existing dataset from {csv_path}")
    df = pd.read_csv(csv_path)
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], utc=True)

    logger.info("Fetching latest data point from CoinGecko")
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": 1}
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the latest data point
    latest_price = data['prices'][-1]
    latest_cap = data['market_caps'][-1]
    latest_volume = data['total_volumes'][-1]

    # Build a single-row DataFrame
    latest_data = pd.DataFrame({
        'snapped_at': [pd.to_datetime(latest_price[0], unit='ms', utc=True)],
        'price': [latest_price[1]],
        'market_cap': [latest_cap[1]],
        'total_volume': [latest_volume[1]]
    })

    logger.info(f"Latest data point: {latest_data.iloc[0].to_dict()}")

    # Check if this timestamp already exists
    if latest_data['snapped_at'].iloc[0] in df['snapped_at'].values:
        logger.info("Latest data point is already in the dataset. No update needed.")
    else:
        logger.info("Appending new data point to the dataset.")
        df = pd.concat([df, latest_data], ignore_index=True)
        df = df.sort_values('snapped_at')
        df.to_csv(csv_path, index=False)
        logger.info(f"Dataset updated and saved to {csv_path}")


# --------------------------------------------------------------------
# Feature Engineering
# --------------------------------------------------------------------
def technical_features(df: pd.DataFrame):
    """
    Adds feature-engineered columns to the DataFrame:
    - Daily returns
    - Rolling means
    - Rolling volatility

    :param df: Cleaned DataFrame
    :return: DataFrame with new feature columns
    """
    logger.info("Adding technical feature columns")

    # Daily returns
    df['returns'] = df['price'].pct_change()

    # Rolling means
    df['SMA_7'] = df['price'].rolling(window=7).mean()
    df['SMA_30'] = df['price'].rolling(window=30).mean()

    # Rolling volatility (std dev)
    df['volatility_7'] = df['price'].rolling(window=7).std()
    df['volatility_30'] = df['price'].rolling(window=30).std()

    # Lag features (previous day's price)
    df['lag_1day'] = df['price'].shift(1)

    logger.info("Feature engineering complete")
    return df


# --------------------------------------------------------------------
# Sequence Generator for LSTM
# --------------------------------------------------------------------

from sklearn.preprocessing import MinMaxScaler
import numpy as np

def generate_sequences(df: pd.DataFrame, feature: str = 'price', window_size: int = 60):
    """
    Generate sequences and targets for LSTM from a cleaned DataFrame.

    :param df: Cleaned DataFrame with a datetime index and numeric columns
    :param feature: Column name to predict (default='price')
    :param window_size: Number of timesteps per input sequence
    :return: X (sequences), y (targets), scaler object
    """
    logger.info(f"Generating sequences using feature '{feature}' with window size {window_size}")

    # Extract the feature column
    series = df[feature].values.reshape(-1, 1)

    # Scale the data between 0 and 1
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series)

    X, y = [], []
    for i in range(window_size, len(scaled)):
        X.append(scaled[i - window_size:i])
        y.append(scaled[i])

    X = np.array(X)
    y = np.array(y)

    logger.info(f"Generated {X.shape[0]} sequences of shape {X.shape[1:]}")

    return X, y, scaler
