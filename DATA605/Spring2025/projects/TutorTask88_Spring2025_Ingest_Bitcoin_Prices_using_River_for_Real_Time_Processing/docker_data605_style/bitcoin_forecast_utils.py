"""
bitcoin_forecast_utils.py

Enhanced utility functions for real-time Bitcoin price streaming using River.
Includes:
- API retry with broader exception handling
- Feature normalization
- Volatility features
- Visualization utilities
- Improved logging and typo fixes
- Self test improvements
"""

import pandas as pd
import logging
import requests
import time
import functools
from sklearn.model_selection import train_test_split
from pathlib import Path
from collections import deque
import matplotlib.pyplot as plt
from river import linear_model, metrics, preprocessing


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Split the dataset into train and test sets
# -----------------------------------------------------------------------------

def split_data(df: pd.DataFrame, target_column: str, test_size: float = 0.2):
    logger.info("Splitting data into train and test sets")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=42)

# -----------------------------------------------------------------------------
# Retry Decorator for API Rate Limits and Transient Errors
# -----------------------------------------------------------------------------

def retry_on_rate_limit(max_retries=5, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.HTTPError,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout) as e:
                    logger.warning(f"Transient error: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    retries += 1
                    current_delay *= 2
                except requests.exceptions.RequestException as e:
                    logger.error(f"Non-retryable error: {e}")
                    break
            raise Exception("Max retries exceeded.")
        return wrapper
    return decorator

# -----------------------------------------------------------------------------
# Function to Get Current Bitcoin Price with Retry Logic
# -----------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
@retry_on_rate_limit()
def get_bitcoin_price_with_retry():
    retries = 5
    delay = 2
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()["bitcoin"]["usd"]
        except Exception as e:
            print(f"bitcoin_forecast_utils:Transient error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

    raise RuntimeError("Failed to fetch Bitcoin price after multiple retries.")

# -----------------------------------------------------------------------------
# Function to Get OHLC Data with Caching
# -----------------------------------------------------------------------------

def get_coin_ohlc(coin_id="bitcoin", vs_currency="usd", days=7, cache_path="cached_ohlc.csv"):
    cache = Path(cache_path)
    if cache.exists():
        logger.info("Loading cached OHLC data")
        df = pd.read_csv(cache_path)
    else:
        logger.info("Fetching OHLC data from CoinGecko API")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
        params = {"vs_currency": vs_currency, "days": days}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.to_csv(cache_path, index=False)

    assert not df.empty, "OHLC DataFrame is empty. API may have failed."
    assert "timestamp" in df.columns, "Missing 'timestamp' column in OHLC data."
    assert df["timestamp"].is_monotonic_increasing, "Timestamps are not in order."
    return df

# -----------------------------------------------------------------------------
# Feature Builders and Normalizers
# -----------------------------------------------------------------------------

def build_rolling_features(prices):
    features = {}
    for i in range(len(prices)):
        features[f"price_lag_{i}"] = prices[-(i + 1)]
    return features

def extract_ohlc_features(ohlc_df: pd.DataFrame) -> pd.DataFrame:
    df = ohlc_df.copy()
    df["range"] = df["high"] - df["low"]
    df["price_change"] = df["close"] - df["open"]
    df["price_change_pct"] = df["price_change"] / df["open"]
    df["volatility"] = df["range"].rolling(window=5).std()
    return df

def initialize_model():
    """
    Initialize a normalized linear regression model with MAE metric.
    The StandardScaler ensures lagged price features are scaled for stability.
    """
    model = preprocessing.StandardScaler() | linear_model.LinearRegression()
    metric = metrics.MAE()
    return model, metric

def build_combined_features(prices, ohlc_features_df):
    """
    Combine price lag features and technical indicators from OHLC.
    Assumes both are aligned in time.
    """
    features = build_rolling_features(prices)
    
    if ohlc_features_df is not None and not ohlc_features_df.empty:
        # Match last timestamp
        latest_ohlc = ohlc_features_df.iloc[-1]
        for col in ["range", "price_change", "price_change_pct", "volatility"]:
            features[col] = latest_ohlc[col]
    
    return features

# -----------------------------------------------------------------------------
# Visualization Utilities
# -----------------------------------------------------------------------------

def plot_ohlc_summary(df: pd.DataFrame):
    df[["open", "high", "low", "close"]].plot(figsize=(10, 5), title="OHLC Summary")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_rolling_price(price_list):
    plt.plot(price_list)
    plt.title("Rolling Price Trend")
    plt.xlabel("Time Step")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Dashboard-Friendly Wrapper Function
# -----------------------------------------------------------------------------

def fetch_bitcoin_data_structured(vs_currency="usd"):
    price = get_bitcoin_price_with_retry(vs_currency)
    ohlc_data = get_coin_ohlc("bitcoin", vs_currency=vs_currency, days=7)
    return {
        "current_price": price,
        "ohlc": ohlc_data
    }

def summarize_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    return df[["open", "high", "low", "close"]].describe()

# -----------------------------------------------------------------------------
# Self test
# -----------------------------------------------------------------------------

def self_test():
    try:
        data = fetch_bitcoin_data_structured()
        logger.info(f"Self test passed. Current BTC price: {data['current_price']}")
    except Exception as e:
        logger.exception("Self test failed")