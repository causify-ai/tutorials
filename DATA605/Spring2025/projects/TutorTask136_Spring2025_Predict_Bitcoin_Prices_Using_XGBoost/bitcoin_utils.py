"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import yfinance as yf
import pandas as pd
import logging
import requests

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_crypto_data(ticker: str = "BTC-USD", start_date: str = "2014-09-17", save_path: str = "BTC-USD-Historical.xlsx") -> pd.DataFrame:
    """
    Downloads historical data for the specified cryptocurrency ticker from Yahoo Finance
    and optionally saves it to an Excel file.

    Args:
        ticker (str): The ticker symbol (default is "BTC-USD").
        start_date (str): The start date for historical data.
        save_path (str): The file path to save the Excel file.

    Returns:
        pd.DataFrame: DataFrame containing the historical data.
    """
    logger.info(f"Starting download for {ticker} from {start_date}")
    try:
        data = yf.download(ticker, start=start_date)
        if data.empty:
            logger.warning(f"No data was downloaded for {ticker}.")
        else:
            data.to_excel(save_path)
            logger.info(f"Data for {ticker} saved to {save_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to download or save data for {ticker}: {e}")
        raise


def fetch_historical_bitcoin(days: int = 365) -> pd.DataFrame:
    """
    Fetch daily historical Bitcoin data for the past `days` from CoinGecko API.
    
    Returns:
        pd.DataFrame: A DataFrame with columns: open, high, low, close, volume indexed by Date.
    """
    logger.info(f"Fetching historical Bitcoin data for the past {days} days from CoinGecko API.")

    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info("Data successfully fetched from CoinGecko.")

        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])

        if not prices or not volumes:
            logger.warning("Received empty data from CoinGecko API.")
            return pd.DataFrame()

        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = df['high'] = df['low'] = df['close'] = df['price']

        volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')

        df = df.merge(volume_df, on='timestamp', how='left')
        df.rename(columns={'timestamp': 'Date'}, inplace=True)
        df.set_index('Date', inplace=True)

        logger.info("Bitcoin data successfully transformed into DataFrame.")

        return df[['open', 'high', 'low', 'close', 'volume']]

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while processing Bitcoin data: {e}")
        raise


