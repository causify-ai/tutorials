#!/usr/bin/env python
"""
Module for loading and preparing Bitcoin price data from Yahoo Finance.

Historical data is fetched using the yfinance library, cleaned, and saved to a CSV file.
"""

import yfinance as yf
import pandas as pd
import utils.logger as logger

# Set up the logger for this module
_LOG = logger.setup(log_file="bitcoin_data_loader.log", enable_console=False)


def load_data(
    ticker: str = "BTC-USD",
    start_date: str = "2014-09-17",
    end_date: str = "2025-04-29",
) -> pd.DataFrame:
    """
    Fetch historical Bitcoin OHLCV data from Yahoo Finance.

    :param ticker: The ticker symbol for the cryptocurrency
    :param start_date: The start date in 'YYYY-MM-DD' format
    :param end_date: The end date in 'YYYY-MM-DD' format
    :return: DataFrame containing the cleaned OHLCV data
    """
    try:
        # Fetch historical data for the given ticker symbol
        btc = yf.Ticker(ticker)
        df = btc.history(start=start_date, end=end_date, interval="1d")
        _LOG.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
        _LOG.info(f"Data shape: {df.shape}")
        return df
    except Exception as e:
        _LOG.error(f"Error fetching data: {e}")
        raise


def clean_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean the DataFrame and check for missing dates in the time series.

    :param df: DataFrame containing the historical data
    :return: Cleaned DataFrame
    """
    try:
        # Remove columns not relevant for Bitcoin
        df = df.drop(columns=["Dividends", "Stock Splits"], errors="ignore")
        # Check for missing values
        missing_values = df.isna().any()
        if missing_values.any():
            _LOG.warning(f"Missing values found in DataFrame: {df.isna().sum()}")
            df = df.dropna()
        return df
    except Exception as e:
        _LOG.error(f"Error cleaning data: {e}")
        raise


def save_data(
    df: pd.DataFrame,
    file_path: str = "data/bitcoin_yahoo_data.csv",
) -> None:
    """
    Save the cleaned DataFrame to a CSV file.

    :param df: DataFrame to save
    :param file_path: Path to save the CSV file
    """
    try:
        df.to_csv(file_path, index=True)
        _LOG.info(f"Data saved to {file_path}")
    except Exception as e:
        _LOG.error(f"Error saving data: {e}")
        raise


if __name__ == "__main__":
    try:
        data = load_data()
        cleaned_data = clean_data(data)
        save_data(cleaned_data)
    except Exception as e:
        _LOG.error(f"An error occurred: {e}")
