"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import pandas as pd
import numpy as np
import logging
import requests
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from prophet import Prophet
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

 
# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# KuCoin API Functions
# -----------------------------------------------------------------------------

def fetch_bitcoin_data_kucoin(days: int = 7, interval: str = '15min') -> pd.DataFrame:
    """
    Fetch historical Bitcoin OHLCV data from KuCoin API.
    
    Args:
        days: Number of days of historical data to fetch
        interval: 15 minute intervals
    
    Returns:
        DataFrame with timestamp, open, high, low, close, volume
    """
    endpoint = "https://api.kucoin.com/api/v1/market/candles"
    symbol = "BTC-USDT"

    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        logger.info(f"Fetching {days} days of BTC data from KuCoin ({interval} candles)")
        
        # API request
        params = {
            'symbol': symbol,
            'type': interval,
            'startAt': int(start_time.timestamp()),
            'endAt': int(end_time.timestamp())
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        # Error Handling
        if data['code'] != '200000':
            raise ValueError(f"API Error: {data.get('msg', 'Unknown error')}")
            
        if not data['data']:
            raise ValueError("No data returned from API")

        candles = data['data']
        df = pd.DataFrame(candles, columns=[
            'timestamp', 'open', 'close', 'high', 'low', 'volume', 'turnover'
        ])
        
        # Convert and sort data
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].astype(float)
        
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Data processing error: {str(e)}")
        raise



def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    """Save DataFrame to CSV with validation"""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
        
    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")
    
    logger.info(f"Saving {len(df)} records to {filename}")
    df.to_csv(filename, index=False)



def load_cleaned_data(file_path: str = 'bitcoin_price_analysis_using_OpenRefine.csv') -> pd.DataFrame:
    """
    Load and validate cleaned Bitcoin price data from CSV.
    
    Args:
        file_path: Path to cleaned CSV file
    
    Returns:
        Cleaned DataFrame with validated columns
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Loading cleaned data from {file_path}")
    
    try:
        # Load CSV with timestamp parsing
        df = pd.read_csv(file_path, parse_dates=['timestamp'])
        
        # Validate required columns
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns: {required_cols}")
            
        logger.info(f"Successfully loaded {len(df)} records")
        return df.sort_values('timestamp')
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise



def validate_cleaned_data(df: pd.DataFrame) -> bool:
    """Validate cleaned Bitcoin data and return status"""
    
    logger = logging.getLogger(__name__)

    # Passing Validation Checks
    checks = {
        "No missing values": lambda: not df[['open', 'high', 'low', 'close']].isnull().any().any(),
        "Valid price relationships": lambda: (df['price_validation'] == 'Valid').all(),
        "Time sequence valid": lambda: df['timestamp'].is_monotonic_increasing
    }
    
    all_passed = True
    for check_name, check_func in checks.items():
        try:
            assert check_func(), check_name
            logger.info(f"{check_name}")
        except AssertionError:
            logger.error(f"Failed: {check_name}")
            failed_checks.append(check_name)
            all_passed = False
            
    if all_passed:
        logger.info("All data validation checks passed successfully!")
    else:
        logger.error("Data validation failed Failed checks: " + ", ".join(failed_checks))
        
    return all_passed



def resample_data(df: pd.DataFrame, interval: str = '1H') -> pd.DataFrame:
    """Resample time series data"""

    # Converting the data from 15m intervals to Hourly Intervals
    resampled = df.resample(interval, on='timestamp').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    return resampled



def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for Bitcoin price analysis.
    
    Args:
        df: DataFrame with 'timestamp', 'open', 'high', 'low', 'close', 'volume'
    
    Returns:
        DataFrame with added technical indicators
    """
    df = df.copy()
    
    # Computing 7-period and 24-period Moving Averages (ma)
    df['ma_7'] = df['close'].rolling(window=7, min_periods=1).mean()
    df['ma_24'] = df['close'].rolling(window=24, min_periods=1).mean()
    
    # Bollinger Bands
    df['std_dev'] = df['close'].rolling(window=20).std()
    df['upper_band'] = df['ma_24'] + (df['std_dev'] * 2)
    df['lower_band'] = df['ma_24'] - (df['std_dev'] * 2)
    
    # Daily volatility
    df['intraday_volatility'] = df['high'] - df['low']

    # Daily Momentum
    df['daily_momentum'] = df['close'].pct_change(periods=96) * 100
    
    return df.dropna()



def plot_technical_indicators(df: pd.DataFrame) -> None:
    """
    Plot Bitcoin price with Moving Averages and Bollinger Bands.

    Args:
        df: DataFrame containing 'timestamp', 'close', 'ma_7', 'ma_24', 'upper_band', 'lower_band'
    """
    
    required_cols = ['timestamp', 'close', 'ma_7', 'ma_24', 'upper_band', 'lower_band']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    fig = go.Figure()

    # Close Price
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['close'],
        mode='lines',
        name='Close Price',
        line=dict(width=2, color='blue')
    ))

    # 7-Period MA
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['ma_7'],
        mode='lines',
        name='7-Period MA',
        line=dict(width=2, dash='dash', color='red')
    ))

    # 24-Period MA
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['ma_24'],
        mode='lines',
        name='24-Period MA',
        line=dict(width=2, dash='dash', color='green')
    ))

    # Bollinger Bands fill
    fig.add_trace(go.Scatter(
        x=pd.concat([df['timestamp'], df['timestamp'][::-1]]),
        y=pd.concat([df['upper_band'], df['lower_band'][::-1]]),
        fill='toself',
        fillcolor='rgba(128, 128, 128, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name='Bollinger Bands'
    ))

    fig.update_layout(
        title='Bitcoin Price with Moving Averages and Bollinger Bands',
        xaxis_title='Timestamp',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        legend=dict(font=dict(size=12)),
        template='plotly_white',
        width=1000,
        height=600
    )

    fig.show()
    


def prepare_forecast_data(df: pd.DataFrame) -> pd.DataFrame:
    
    """Prepare DataFrame for Prophet forecasting"""
    
    return df[['timestamp', 'close']].rename(columns={
        'timestamp': 'ds',
        'close': 'y'
    })



def train_model(df: pd.DataFrame, periods: int = 96) -> tuple:
    """
    Train Prophet model and generate forecasts.
    
    Args:
        df: DataFrame with 'ds' (datetime) and 'y' (price)
        periods: Number of 15-minute intervals to forecast (96 = 24h)
    
    Returns:
        model: Trained Prophet model
        forecast: DataFrame with predictions
    """

    logger.info("Starting model training...")
    
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=False,
        yearly_seasonality=False
    )
    model.fit(df)
    
    future = model.make_future_dataframe(
        periods=periods, 
        freq='15min',
        include_history=False
    )
    forecast = model.predict(future)
    
    return model, forecast



def plot_forecast(train_df: pd.DataFrame, forecast_df: pd.DataFrame) -> None:
    """
    Plot the Bitcoin forecasted prices for the last 24 hours using interactive Plotly.

    Args:
        train_df (pd.DataFrame): Historical training data with columns 'ds' and 'y'.
        forecast_df (pd.DataFrame): Forecast output from the Prophet model, including 
                                    'ds', 'yhat', 'yhat_lower', and 'yhat_upper'.
    """
    
    fig = go.Figure()

    # Actual (Historical) Prices
    fig.add_trace(go.Scatter(
        x=train_df['ds'],
        y=train_df['y'],
        mode='lines',
        name='Actual Price',
        line=dict(color='blue')
    ))

    # Forecasted Prices
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))

    # Confidence Interval
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df['ds'], forecast_df['ds'][::-1]]),
        y=pd.concat([forecast_df['yhat_upper'], forecast_df['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(128, 128, 128, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name='Confidence Interval'
    ))

    fig.update_layout(
        title='Bitcoin Price Forecast (24 Hours)',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        legend=dict(font=dict(size=12)),
        hovermode='x unified',
        template='plotly_white',
        width=1000,
        height=600
    )

    fig.show()



def plot_comparision(test_df: pd.DataFrame, forecast_df: pd.DataFrame) -> None:
    """
    Plotting the Actual vs Predicted(Forecasted) Bitcoin prices using Plotly.

    Args:
        test_df: DataFrame with 'ds' and 'y' columns (actual values).
        forecast_df: DataFrame with 'ds', 'yhat', 'yhat_lower', 'yhat_upper' columns (predicted values).
    """
    comparison_df = pd.merge(
        test_df[['ds', 'y']], 
        forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], 
        on='ds', 
        how='inner'
    )

    fig = go.Figure()

    # Actual Prices
    fig.add_trace(go.Scatter(
        x=comparison_df['ds'], 
        y=comparison_df['y'], 
        mode='lines+markers', 
        name='Actual Price',
        line=dict(color='blue')
    ))

    # Predicted Prices
    fig.add_trace(go.Scatter(
        x=comparison_df['ds'], 
        y=comparison_df['yhat'], 
        mode='lines+markers', 
        name='Predicted Price',
        line=dict(color='orange', dash='dash')
    ))

    # Confidence Interval
    fig.add_trace(go.Scatter(
        x=pd.concat([comparison_df['ds'], comparison_df['ds'][::-1]]),
        y=pd.concat([comparison_df['yhat_upper'], comparison_df['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(128, 128, 128, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='Confidence Interval'
    ))

    fig.update_layout(
        title='Interactive Actual vs Predicted Bitcoin Prices',
        xaxis_title='Timestamp',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        legend=dict(font=dict(size=12)),
        template='plotly_white',
        width=1000,
        height=500
    )

    fig.show()





