"""
This file contains utlility functions for the project.

Functions include:

- logging_setup: Sets up the logger with customizable handlers for console and file output.
- load_yahoo_data: Fetches historical Bitcoin OHLCV data from Yahoo Finance.
- clean_yahoo_data: Cleans the historical Bitcoin data fetched from Yahoo Finance.
- save_to_csv: Saves the DataFrame to a CSV file.
- localize_to_timezone: Converts a naive datetime or string to a timezone-aware pandas Timestamp.
- split_yahoo_data: Splits the DataFrame into training, testing, and validation sets.
- calculate_features: Computes a suite of features on the DataFrame, including log returns and simple moving averages.
- calculate_normalization_params: Calculates normalization parameters for specified columns in the DataFrame.
"""

import os
import logging
import numpy as np
import pandas as pd
import yfinance as yf


# #############################################################################
# Logging Setup
# #############################################################################
def logging_setup(
    log_level: int = logging.INFO,
    log_file: str = "default.log",
    enable_console: bool = True,
    enable_file: bool = True,
):
    """
    Sets up the logger.

    This function configures the logger with customizable handlers for console and file output.
    Supports all standard logging levels: DEBUG, INFO, WARN, ERROR, and CRITICAL.

    :param log_level: The minimum logging level (DEBUG, INFO, WARN, ERROR, CRITICAL). Defaults to INFO
    :param log_file: The file to which logs will be written. Defaults to 'bitcoin_rl_agent.log'
    :param enable_console: Whether to enable console logging. Defaults to True
    :param enable_file: Whether to enable file logging. Defaults to True
    :return: The logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    # Clear any existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    # Define log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # Create and add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    # Create and add file handler if enabled
    if enable_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    # Ensure logs propagate up to the root logger
    logger.propagate = True
    return logger


# Set up the logger for the utility functions
_LOG = logging_setup()


# #############################################################################
# Data Loading (from Yahoo Finance)
# #############################################################################
def load_yahoo_data(
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


# #############################################################################
# Data Cleaning (for Yahoo Finance data)
# #############################################################################
def clean_yahoo_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean the historical Bitcoin data fetched from Yahoo Finance.
    This function removes unnecessary columns and handles missing values.

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
        if df.index.tzinfo is not None:
            _LOG.info(f"DataFrame timezone: {df.index.tzinfo}")
        else:
            _LOG.info("DataFrame has no timezone")
        return df
    except Exception as e:
        _LOG.error(f"Error cleaning data: {e}")
        raise


# #############################################################################
# Save DataFrame to CSV
# #############################################################################
def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
    Save the DataFrame to a CSV file.

    :param df: DataFrame to save
    :param file_path: Path to the CSV file
    :param save_index: Whether to save the DataFrame index to the CSV file
    :return: None
    """
    try:
        os.makedirs("data", exist_ok=True)
        df.to_csv(file_path)
        _LOG.info(f"Data saved to {file_path}")
    except Exception as e:
        _LOG.error(f"Error saving data to CSV: {e}")
        raise


# #############################################################################
# Localize datetime to DataFrame timezone
# #############################################################################
def localize_to_timezone(input_date: str, timezone: str) -> pd.Timestamp:
    """
    Convert a naive datetime or string to a timezone-aware pandas Timestamp.

    :param input_date: The input date, either as a datetime object or a string
    :param timezone: The timezone to localize to (e.g., 'UTC', 'America/New_York')
    :return: A timezone-aware pandas Timestamp
    """
    return pd.to_datetime(input_date).tz_localize(timezone)


# #############################################################################
# Data Split for Training, Validation, and Testing
# #############################################################################
def split_yahoo_data(
    df: pd.DataFrame,
    train_start_date: str = "2014-09-17",
    validation_start_date: str = "2022-02-21",
    test_start_date: str = "2024-01-01",
    train_data_path: str = "data/train_data.csv",
    validation_data_path: str = "data/validation_data.csv",
    test_data_path: str = "data/test_data.csv",
) -> None:
    """
    Split the DataFrame into training, testing, and validation sets.

    :param df: DataFrame containing the historical data
    :param train_start_date: Start date for the training set
    :param validation_start_date: Start date for the validation set
    :param test_start_date: Start date for the testing set
    :param train_data_path: Path to save the training data
    :param validation_data_path: Path to save the validation data
    :param test_data_path: Path to save the testing data
    """
    try:
        # Check if DataFrame index has timezone information
        has_tz = df.index.tzinfo is not None
        if has_tz:
            # If DataFrame has timezone, localize the input dates to match
            train_start_date = localize_to_timezone(train_start_date, df.index.tzinfo)
            validation_start_date = localize_to_timezone(
                validation_start_date, df.index.tzinfo
            )
            test_start_date = localize_to_timezone(test_start_date, df.index.tzinfo)
        else:
            _LOG.info("DataFrame has no timezone")
            # If DataFrame has no timezone, keep dates timezone-naive
            train_start_date = pd.to_datetime(train_start_date)
            validation_start_date = pd.to_datetime(validation_start_date)
            test_start_date = pd.to_datetime(test_start_date)
        _LOG.info(
            f"Train start: {train_start_date}, Validation start: {validation_start_date}, Test start: {test_start_date}"
        )
        # Split the data into training, validation, and testing sets
        train_data = df.loc[
            train_start_date : validation_start_date - pd.Timedelta(days=1)
        ]
        validation_data = df.loc[
            validation_start_date : test_start_date - pd.Timedelta(days=1)
        ]
        test_data = df.loc[test_start_date:]
        _LOG.info(
            f"Train shape: {train_data.shape}, Validation shape: {validation_data.shape}, Test shape: {test_data.shape}"
        )
        # Save the split data to CSV files
        save_to_csv(train_data, train_data_path)
        save_to_csv(validation_data, validation_data_path)
        save_to_csv(test_data, test_data_path)
    except Exception as e:
        _LOG.error(f"Error splitting data: {e}")
        raise


# #############################################################################
# Feature Calculation (Log Returns and SMAs)
# #############################################################################
def calculate_features(
    df: pd.DataFrame,
    price_sma_windows: dict = {"Price_SMA_20": 20},
    volume_sma_windows: dict = {"Volume_SMA_20": 20},
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Compute a suite of features on the DataFrame, including log returns and simple moving averages.

    :param df: DataFrame with 'Close' and 'Volume' columns and datetime index
    :param price_sma_windows: dict mapping column names to price SMA window sizes, e.g., {'Price_SMA_20': 20}
    :param volume_sma_windows: dict mapping column names to volume SMA window sizes, e.g., {'Volume_SMA_20': 20}
    :param drop_na: whether to drop rows with NaN after feature calculations
    :return: DataFrame with new feature columns added
    """
    try:
        # Create a copy to avoid modifying the original
        df = df.copy()
        # Compute log returns for price
        df["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))
        # Compute price SMAs
        for name, window in price_sma_windows.items():
            df[name] = df["Close"].rolling(window=window).mean()
        # Compute volume SMAs
        for name, window in volume_sma_windows.items():
            df[name] = df["Volume"].rolling(window=window).mean()
        # Remove rows with missing values if required
        if drop_na:
            df = df.dropna()
        _LOG.info(f"Data shape after feature calculation: {df.shape}")
        return df
    except Exception as e:
        _LOG.error(f"Error calculating features: {e}")
        raise


# #############################################################################
# Normalization Parameters Calculation
# #############################################################################
def calculate_normalization_params(
    df: pd.DataFrame,
    columns: list,
    method: str = "zscore",
) -> dict:
    """
    Calculate normalization parameters for the specified columns in the DataFrame.

    :param df: DataFrame containing the data
    :param columns: List of columns to calculate parameters for
    :param method: Normalization method ('minmax' or 'zscore')
    :return: Dictionary of normalization parameters for each column
    """
    try:
        params = {}
        if method == "minmax":
            for col in columns:
                min_val = df[col].min()
                max_val = df[col].max()
                params[col] = {"min": min_val, "max": max_val}
                _LOG.info(f"Column {col} - Min: {min_val}, Max: {max_val}")
        elif method == "zscore":
            for col in columns:
                mean = df[col].mean()
                std = df[col].std()
                params[col] = {"mean": mean, "std": std}
                _LOG.info(f"Column {col} - Mean: {mean}, Std: {std}")
        else:
            raise ValueError(f"Unsupported normalization method: {method}")
        return params
    except Exception as e:
        _LOG.error(f"Error calculating normalization parameters: {e}")
        raise


# #############################################################################
# Normalize Data
# #############################################################################
def normalize_data(dataframes: list, params: dict) -> tuple:
    """
    Normalize the training, validation, and test data using the calculated parameters.

    :param dataframes: List of DataFrames to normalize
    :param params: Dictionary of normalization parameters
    :return: Tuple of normalized DataFrames
    """
    try:
        for col, stat in params.items():
            if "min" in stat:
                min_val = stat["min"]
                max_val = stat["max"]
                for df in dataframes:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
            elif "mean" in stat:
                mean = stat["mean"]
                std = stat["std"]
                for df in dataframes:
                    df[col] = (df[col] - mean) / std
        _LOG.info(
            f"Data normalization complete. Data shapes: {[df.shape for df in dataframes]}"
        )
        return dataframes[0], dataframes[1], dataframes[2]
    except Exception as e:
        _LOG.error(f"Error normalizing data: {e}")
        raise
