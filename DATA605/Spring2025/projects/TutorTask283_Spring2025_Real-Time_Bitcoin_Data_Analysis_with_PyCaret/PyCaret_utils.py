# PyCaret_utils.py

import logging
import requests
import pandas as pd
import numpy as np
from pycaret.time_series import setup, compare_models, finalize_model, predict_model

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Wrapper
class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()
        logger.info("Initialized CoinGecko API session.")

    def get_ohlc(self, coin_id="bitcoin", vs_currency="usd", days="max"):
        endpoint = f"{self.BASE_URL}/coins/{coin_id}/ohlc"
        params = {"vs_currency": vs_currency, "days": days}
        logger.info(f"Requesting OHLC data from CoinGecko for {coin_id} in {vs_currency} over {days} days.")

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            logger.info(f"Fetched {len(df)} records from CoinGecko API.")
            return df
        except Exception as e:
            logger.error(f"API Error: {e}")
            raise

def fetch_and_validate_data(client, days=90):
    logger.info("Fetching and validating data from API client.")
    raw_data = client.get_ohlc(days=days)

    assert isinstance(raw_data, pd.DataFrame), "Data fetched is not a DataFrame."
    assert not raw_data.empty, "Fetched data is empty."
    assert {'open', 'high', 'low', 'close'}.issubset(raw_data.columns), "Missing required OHLC columns."

    data = raw_data[~raw_data.index.duplicated(keep='first')].copy()
    logger.info("Calculating derived metrics: daily return, 7-day volatility, and 14-day EMA volume.")
    data['daily_return'] = data['close'].pct_change()
    data['volatility_7d'] = data['daily_return'].rolling(7).std()
    data['volume_ema_14'] = data['close'].ewm(span=14).mean()
    logger.info(f"Data shape after processing: {data.shape}")
    return data

def prepare_data_for_pycaret(data):
    logger.info("Preparing data for PyCaret.")
    formatted = data[['close']].copy()
    formatted = formatted.asfreq('D').ffill()
    logger.info("Data formatted with daily frequency and forward-filled missing values.")
    return formatted

def run_pycaret_experiment(data):
    logger.info("Running PyCaret setup for time series forecasting.")
    if not isinstance(data.index, pd.DatetimeIndex):
        logger.error("Data index is not datetime.")
        raise ValueError("Index must be datetime")

    numeric_data = data.select_dtypes(include=np.number).dropna()
    exp = setup(
        data=numeric_data,
        target='close',
        fold_strategy='expanding',
        fold=3,
        numeric_imputation_target='ffill',
        session_id=42,
        fh=7,
        verbose=True
    )
    logger.info("PyCaret setup completed.")
    return exp

def forecast_best_model():
    logger.info("Comparing models using PyCaret.")
    best_model = compare_models()
    logger.info(f"Best model selected: {best_model}")
    final_model = finalize_model(best_model)
    logger.info("Final model trained and ready for prediction.")
    future_predictions = predict_model(final_model)
    logger.info("Future predictions generated.")
    return best_model, future_predictions

def add_lag_features(df, lags=[1, 2, 3]):
    logger.info(f"Adding lag features: {lags}")
    for lag in lags:
        df[f'lag_{lag}'] = df['close'].shift(lag)
    logger.info("Lag features added.")
    return df.dropna()
