"""
tfp.utils.py

This file contains utility functions for Bitcoin price forecasting with TensorFlow Probability.
It includes functions for data collection, preprocessing, timestamp handling, and dashboard visualization.

Functions are organized by category with proper documentation including parameter types and descriptions.
"""

import pandas as pd
import numpy as np
import logging
import os
import time
import traceback
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, List, Union, Optional, Any
import yaml

# -----------------------------------------------------------------------------
# Logging Functions
# -----------------------------------------------------------------------------

def get_logger(name: str, log_level: Optional[Union[str, int]] = None) -> logging.Logger:
    """
    Get a logger with the specified name and log level.
    
    :param name: name of the logger
    :param log_level: log level (e.g., 'INFO', 'DEBUG', etc.) or None to use default
    :return: configured logger instance
    """
    # Set default log level to INFO if not specified
    if log_level is None:
        level = logging.INFO
    elif isinstance(log_level, str):
        # Convert string log level to logging constant
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        # Use the provided level directly
        level = log_level
    
    # Configure root logger if not already configured
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s.%(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get the logger and set its level
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    return logger

# Default logger for this module
logger = get_logger(__name__)

# -----------------------------------------------------------------------------
# Timestamp Handling Functions
# -----------------------------------------------------------------------------

def parse_timestamp(ts: Any) -> Optional[datetime]:
    """
    Parse a timestamp string or number to a datetime object (UTC).

    :param ts: Timestamp as string, int, or float
    :return: datetime object in UTC, or None if parsing fails
    """
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        return pd.to_datetime(ts, utc=True).to_pydatetime()
    except Exception:
        return None

def format_timestamp(dt: datetime, use_t_separator: bool = True) -> str:
    """
    Format a datetime object to ISO8601 string with optional 'T' separator.

    :param dt: datetime object
    :param use_t_separator: Whether to use 'T' as date-time separator
    :return: ISO8601 formatted string
    """
    if not dt:
        return ''
    if use_t_separator:
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def to_iso8601(dt: Any) -> str:
    """
    Convert a datetime or timestamp to ISO8601 string with 'T' separator.

    :param dt: datetime object or timestamp
    :return: ISO8601 formatted string
    """
    if isinstance(dt, str):
        dt = parse_timestamp(dt)
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt, tz=timezone.utc)
    if isinstance(dt, datetime):
        return format_timestamp(dt, use_t_separator=True)
    return ''

def get_last_update_time(file_path: str) -> Optional[datetime]:
    """
    Get the last modification time of a file.
    
    :param file_path: path to the file
    :return: datetime of last modification or None if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            mod_time = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mod_time)
        return None
    except Exception as e:
        logger.error(f"Error getting file modification time: {e}")
        return None

# -----------------------------------------------------------------------------
# Price Formatting Functions
# -----------------------------------------------------------------------------

def normalize_price(value: Union[float, str, int]) -> float:
    """
    Convert price to USD, rounded to 2 decimal places.
    
    :param value: price value to normalize
    :return: normalized price as float with 2 decimal places
    """
    return round(float(value), 2)

def usd_to_display_str(price: float, decimals: int = 2) -> str:
    """
    Format a price as a USD string.

    :param price: Price value
    :param decimals: Number of decimal places
    :return: Formatted price string
    """
    return f"${price:,.{decimals}f}"

def format_price(price: Union[float, str, int], decimals: int = 2) -> str:
    """
    Format price with specified decimal places.
    
    :param price: price value to format
    :param decimals: number of decimal places
    :return: formatted price string
    """
    try:
        return f"${float(price):.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"

def safe_round(value: Any, decimals: int = 2) -> float:
    """
    Safely round a value to the specified number of decimals.

    :param value: Value to round (float, int, or numpy array)
    :param decimals: Number of decimal places
    :return: Rounded float
    """
    try:
        if isinstance(value, np.ndarray):
            if value.size == 1:
                value = value.item()
            else:
                value = value[0]
        return round(float(value), decimals)
    except Exception:
        return 0.0

# -----------------------------------------------------------------------------
# Data Loading Functions
# -----------------------------------------------------------------------------

def load_and_filter_data(config: Dict, 
                         predictions_file: str, 
                         metrics_file: str, 
                         raw_data_file: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Unified data loader for all dashboards. Returns (predictions, metrics, raw_data) DataFrames.
    
    :param config: application configuration dictionary
    :param predictions_file: path to predictions CSV file
    :param metrics_file: path to metrics CSV file
    :param raw_data_file: path to raw data CSV file
    :return: tuple of (predictions, metrics, raw_data) DataFrames
    """
    try:
        logger.info(f"Loading data from files:")
        logger.info(f"  - Predictions: {predictions_file}")
        logger.info(f"  - Metrics: {metrics_file}")
        logger.info(f"  - Raw data: {raw_data_file}")

        # Check if files exist
        for file_path in [predictions_file, metrics_file, raw_data_file]:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None, None, None

        # Helper for robust date parsing
        def parse_dates_col(col):
            return [parse_timestamp(x) for x in col]

        # Load predictions with retry
        max_retries = 3
        retry_delay = 1  # seconds
        
        predictions = None
        for attempt in range(max_retries):
            try:
                predictions = pd.read_csv(
                    predictions_file,
                    names=config['data_format']['columns']['predictions']['names'],
                    skiprows=1,
                    on_bad_lines='skip'  # Skip bad lines instead of failing
                )
                predictions['timestamp'] = parse_dates_col(predictions['timestamp'])
                logger.info(f"Successfully loaded predictions with {len(predictions)} rows")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt+1}/{max_retries} failed to load predictions: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to load predictions after {max_retries} attempts: {e}\n{traceback.format_exc()}")
                    predictions = pd.DataFrame(columns=config['data_format']['columns']['predictions']['names'])
                time.sleep(retry_delay)
        
        # Load metrics with retry
        metrics = None
        for attempt in range(max_retries):
            try:
                metrics = pd.read_csv(
                    metrics_file,
                    names=config['data_format']['columns']['metrics']['names'],
                    skiprows=1,
                    on_bad_lines='skip'  # Skip bad lines instead of failing
                )
                metrics['timestamp'] = parse_dates_col(metrics['timestamp'])
                logger.info(f"Successfully loaded metrics with {len(metrics)} rows")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt+1}/{max_retries} failed to load metrics: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to load metrics after {max_retries} attempts: {e}\n{traceback.format_exc()}")
                    metrics = pd.DataFrame(columns=config['data_format']['columns']['metrics']['names'])
                time.sleep(retry_delay)
        
        # Load raw data with retry
        raw_data = None
        for attempt in range(max_retries):
            try:
                raw_data = pd.read_csv(
                    raw_data_file,
                    names=config['data_format']['columns']['raw_data']['names'],
                    skiprows=1,
                    on_bad_lines='skip'  # Skip bad lines instead of failing
                )
                raw_data['timestamp'] = parse_dates_col(raw_data['timestamp'])
                logger.info(f"Successfully loaded raw data with {len(raw_data)} rows")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt+1}/{max_retries} failed to load raw data: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to load raw data after {max_retries} attempts: {e}\n{traceback.format_exc()}")
                    raw_data = pd.DataFrame(columns=config['data_format']['columns']['raw_data']['names'])
                time.sleep(retry_delay)
                
        return price_df, pred_df, metrics_df
    except Exception as e:
        logger.error(f"Error in load_data: {e}\n{traceback.format_exc()}")
        return None, None, None

def load_config(path: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    :param path: Path to YAML file
    :return: Configuration dictionary
    """
    with open(path) as f:
        return yaml.safe_load(f)

def get_service_config(service_name: str) -> Dict[str, Any]:
    """
    Load the unified configuration for a given service.

    :param service_name: Name of the service
    :return: Configuration dictionary
    """
    config_path = os.path.join(os.path.dirname(__file__), '../configs/config.yaml')
    config = load_config(config_path)
    return config.get(service_name, config)

# -----------------------------------------------------------------------------
# Dashboard Helper Functions
# -----------------------------------------------------------------------------

def check_cold_start(df: pd.DataFrame, min_points: int = 10) -> bool:
    """
    Check if we're in a cold start situation (not enough data points).
    
    :param df: DataFrame to check
    :param min_points: minimum number of points required
    :return: True if in cold start, False otherwise
    """
    return df is None or len(df) < min_points

def get_current_price(price_df: pd.DataFrame) -> float:
    """
    Get the most recent price from the price DataFrame.
    
    :param price_df: DataFrame containing price data
    :return: most recent price as float
    """
    if price_df is None or len(price_df) == 0:
        return 0.0
    
    try:
        return float(price_df['close'].iloc[-1])
    except (IndexError, KeyError):
        return 0.0

def filter_recent_data(df: pd.DataFrame, minutes: int = 30) -> pd.DataFrame:
    """
    Filter DataFrame to only include data from the last N minutes.
    
    :param df: DataFrame to filter
    :param minutes: number of minutes to include
    :return: filtered DataFrame
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    try:
        # Get the most recent timestamp
        most_recent = df['timestamp'].max()
        
        # Calculate the cutoff time
        cutoff = most_recent - timedelta(minutes=minutes)
        
        # Filter the DataFrame
        return df[df['timestamp'] >= cutoff].copy()
    except Exception as e:
        logger.error(f"Error filtering recent data: {e}")
        return pd.DataFrame()

def calculate_mae(errors: List[float]) -> float:
    """
    Calculate Mean Absolute Error from a list of errors.
    
    :param errors: list of error values
    :return: mean absolute error
    """
    if not errors:
        return 0.0
    
    return np.mean([abs(e) for e in errors])

def rate_mae(mae: float, price: float) -> str:
    """
    Rate the MAE as Good, Fair, or Poor based on percentage of price.
    
    :param mae: mean absolute error value
    :param price: current price for comparison
    :return: rating as string ("Good", "Fair", or "Poor")
    """
    if price <= 0:
        return "Unknown"
    
    # Calculate MAE as percentage of price
    mae_percent = (mae / price) * 100
    
    # Rate based on percentage
    if mae_percent < 0.1:  # Less than 0.1% error
        return "Good"
    elif mae_percent < 0.5:  # Less than 0.5% error
        return "Fair"
    else:
        return "Poor"

# -----------------------------------------------------------------------------
# Data Collection Functions
# -----------------------------------------------------------------------------

def fetch_bitcoin_price(api_url: str = "https://api.coinbase.com/v2/prices/BTC-USD/spot") -> Optional[float]:
    """
    Fetch current Bitcoin price from Coinbase API.
    
    :param api_url: URL of the Coinbase API endpoint
    :return: current Bitcoin price or None if request fails
    """
    import requests
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data['data']['amount'])
        else:
            logger.error(f"API request failed with status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        return None

def detect_outliers(series: np.ndarray, method: str = 'zscore', threshold: float = 3.0) -> List[int]:
    """
    Detect outliers in a time series using various methods.
    
    :param series: numpy array of values
    :param method: detection method ('zscore', 'iqr', or 'percent')
    :param threshold: threshold for outlier detection
    :return: list of indices of outliers
    """
    if len(series) < 3:
        return []
    
    if method == 'zscore':
        # Z-score method
        z_scores = np.abs(stats.zscore(series))
        return np.where(z_scores > threshold)[0].tolist()
    
    elif method == 'iqr':
        # IQR method
        q1 = np.percentile(series, 25)
        q3 = np.percentile(series, 75)
        iqr = q3 - q1
        lower_bound = q1 - (threshold * iqr)
        upper_bound = q3 + (threshold * iqr)
        return np.where((series < lower_bound) | (series > upper_bound))[0].tolist()
    
    elif method == 'percent':
        # Percent change method
        pct_changes = np.abs(np.diff(series) / series[:-1]) * 100
        # Add a 0 at the beginning to match original array length
        pct_changes = np.insert(pct_changes, 0, 0)
        return np.where(pct_changes > threshold)[0].tolist()
    
    return []

def save_to_csv(data: pd.DataFrame, file_path: str, mode: str = 'a') -> bool:
    """
    Save DataFrame to CSV file.
    
    :param data: DataFrame to save
    :param file_path: path to the CSV file
    :param mode: file mode ('a' for append, 'w' for write)
    :return: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if file exists for header
        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
        
        # Write to CSV
        data.to_csv(file_path, mode=mode, header=not file_exists, index=False)
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV {file_path}: {e}")
        return False

# -----------------------------------------------------------------------------
# Visualization Helper Functions
# -----------------------------------------------------------------------------

def create_price_chart(price_df: pd.DataFrame, pred_df: pd.DataFrame, time_window_minutes: int = 30):
    """
    Create a price chart with actual and predicted values using Streamlit.
    
    :param price_df: DataFrame with actual price data
    :param pred_df: DataFrame with prediction data
    :param time_window_minutes: time window to display in minutes
    :return: None (displays chart via Streamlit)
    """
    import streamlit as st
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Filter data to time window
    filtered_price_df = filter_recent_data(price_df, time_window_minutes)
    filtered_pred_df = filter_recent_data(pred_df, time_window_minutes)
    
    # Create figure
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Add price trace
    if len(filtered_price_df) > 0:
        fig.add_trace(
            go.Scatter(
                x=filtered_price_df['timestamp'],
                y=filtered_price_df['close'],
                mode='lines',
                name='Actual Price',
                line=dict(color='blue', width=2)
            )
        )
    
    # Add prediction trace
    if len(filtered_pred_df) > 0:
        fig.add_trace(
            go.Scatter(
                x=filtered_pred_df['timestamp'],
                y=filtered_pred_df['prediction'],
                mode='lines',
                name='Predicted Price',
                line=dict(color='orange', width=2)
            )
        )
        
        # Add confidence interval
        fig.add_trace(
            go.Scatter(
                x=filtered_pred_df['timestamp'].tolist() + filtered_pred_df['timestamp'].tolist()[::-1],
                y=filtered_pred_df['upper'].tolist() + filtered_pred_df['lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255,165,0,0.2)',
                line=dict(color='rgba(255,165,0,0)'),
                name='99% Confidence Interval'
            )
        )
    
    # Update layout
    fig.update_layout(
        title='Bitcoin Price and Prediction',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def create_error_chart(metrics_df: pd.DataFrame, time_window_minutes: int = 30):
    """
    Create an error chart using Streamlit.
    
    :param metrics_df: DataFrame with error metrics
    :param time_window_minutes: time window to display in minutes
    :return: None (displays chart via Streamlit)
    """
    import streamlit as st
    import plotly.graph_objects as go
    
    # Filter data to time window
    filtered_metrics_df = filter_recent_data(metrics_df, time_window_minutes)
    
    if len(filtered_metrics_df) == 0:
        st.warning("No error data available")
        return
    
    # Calculate MAE
    mae = calculate_mae(filtered_metrics_df['error'].tolist())
    
    # Create figure
    fig = go.Figure()
    
    # Add error trace
    fig.add_trace(
        go.Scatter(
            x=filtered_metrics_df['timestamp'],
            y=filtered_metrics_df['error'],
            mode='lines',
            name='Actual Error',
            line=dict(color='blue', width=2)
        )
    )
    
    # Add horizontal line for MAE
    fig.add_trace(
        go.Scatter(
            x=[filtered_metrics_df['timestamp'].min(), filtered_metrics_df['timestamp'].max()],
            y=[mae, mae],
            mode='lines',
            name=f'MAE: {mae:.2f}',
            line=dict(color='red', width=2, dash='dot')
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Prediction Error',
        xaxis_title='Time',
        yaxis_title='Error (USD)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# --- Data Validation Utilities (from data_collector) ---
def validate_bitcoin_price(price: float) -> Tuple[bool, str]:
    """
    Validate Bitcoin price is within a reasonable range.

    :param price: Bitcoin price
    :return: (is_valid, message)
    """
    if not isinstance(price, (int, float)):
        return False, f"Price must be numeric, got {type(price)}"
    if price < 100 or price > 200000:
        return False, f"Bitcoin price {price} outside reasonable range (100-200000)"
    return True, "Price validated"

def check_data_quality(data_point: Dict[str, Any], recent_prices: Optional[List[float]] = None) -> Tuple[bool, str]:
    """
    Check for data quality issues such as missing fields, invalid values, and outliers.

    :param data_point: Data point dictionary
    :param recent_prices: List of recent prices for outlier detection
    :return: (is_valid, message)
    """
    required_fields = ['timestamp', 'close']
    for field in required_fields:
        if field not in data_point or data_point[field] is None:
            return False, f"Missing required field: {field}"
    try:
        if isinstance(data_point['timestamp'], str):
            pd.to_datetime(data_point['timestamp'])
    except Exception:
        return False, f"Invalid timestamp: {data_point['timestamp']}"
    price_valid, price_msg = validate_bitcoin_price(data_point['close'])
    if not price_valid:
        return False, price_msg
    # Outlier detection (simplified)
    if recent_prices and len(recent_prices) >= 5:
        current_price = data_point['close']
        median_price = np.median(recent_prices)
        mad = np.median([abs(p - median_price) for p in recent_prices])
        if mad > 0:
            modified_z = 0.6745 * abs(current_price - median_price) / mad
            if modified_z > 10:
                return False, f"Extreme price outlier detected: {current_price} (z-score: {modified_z:.2f})"
        pct_change = abs(current_price - recent_prices[-1]) / recent_prices[-1]
        if pct_change > 0.20:
            return False, f"Suspicious price jump: {pct_change:.2%} ({recent_prices[-1]} → {current_price})"
    return True, "Data validated"

# --- Dashboard/DataFrame Utilities (from dashboard/app.py) ---
def filter_last_n_minutes(df: pd.DataFrame, n_minutes: int, check_time: bool = True) -> pd.DataFrame:
    """
    Filter a DataFrame to only include data from the last n minutes.

    :param df: Input DataFrame
    :param n_minutes: Number of minutes to filter
    :param check_time: Whether to filter by actual time or just take the last n rows
    :return: Filtered DataFrame
    """
    if df is None or df.empty:
        return df
    df = df.copy()
    if 'timestamp' not in df.columns:
        return df
    df = df.sort_values('timestamp')
    if check_time:
        now = pd.Timestamp.now(tz=None)
        cutoff = now - pd.Timedelta(minutes=n_minutes)
        filtered_df = df[df['timestamp'] >= cutoff]
        if filtered_df.empty:
            n_entries = min(30, len(df))
            filtered_df = df.tail(n_entries)
    else:
        n_entries = min(30, len(df))
        filtered_df = df.tail(n_entries)
    return filtered_df 