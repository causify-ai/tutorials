import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

def calculate_moving_average(data: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculate the moving average for the given window size.
    
    Args:
        data (pd.DataFrame): DataFrame with price data
        window (int): Window size for moving average
        
    Returns:
        pd.Series: Moving average values
    """
    return data['price'].rolling(window=window).mean()

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) technical indicator.
    
    Args:
        data (pd.DataFrame): DataFrame with price data
        window (int): Window size for RSI calculation (default: 14)
        
    Returns:
        pd.Series: RSI values
    """
    # Calculate price changes
    delta = data['price'].diff()
    
    # Separate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Calculate average gain and loss over the specified window
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    # Calculate relative strength
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate the Moving Average Convergence Divergence (MACD) technical indicator.
    
    Args:
        data (pd.DataFrame): DataFrame with price data
        fast_period (int): Window size for fast EMA (default: 12)
        slow_period (int): Window size for slow EMA (default: 26)
        signal_period (int): Window size for signal line (default: 9)
        
    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: MACD line, signal line, and histogram
    """
    # Calculate fast and slow EMAs
    ema_fast = data['price'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = data['price'].ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line (EMA of MACD line)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram (difference between MACD and signal line)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands for the given window and standard deviation.
    
    Args:
        data (pd.DataFrame): DataFrame with price data
        window (int): Window size for moving average (default: 20)
        num_std (float): Number of standard deviations (default: 2.0)
        
    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: Middle band, upper band, and lower band
    """
    # Calculate middle band (simple moving average)
    middle_band = data['price'].rolling(window=window).mean()
    
    # Calculate standard deviation
    std_dev = data['price'].rolling(window=window).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std_dev * num_std)
    lower_band = middle_band - (std_dev * num_std)
    
    return middle_band, upper_band, lower_band

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various technical indicators for the given price data.
    
    Args:
        data (pd.DataFrame): DataFrame with price data
        
    Returns:
        pd.DataFrame: DataFrame with technical indicators
    """
    # Create a copy of the data to avoid modifying the original
    df = data.copy()
    
    # Moving Averages
    df['ma_20'] = calculate_moving_average(df, 20)
    df['ma_50'] = calculate_moving_average(df, 50)
    df['ma_100'] = calculate_moving_average(df, 100)
    
    # RSI
    df['rsi'] = calculate_rsi(df)
    
    # MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df)
    
    # Bollinger Bands
    df['bb_middle'], df['bb_upper'], df['bb_lower'] = calculate_bollinger_bands(df)
    
    # Price momentum (percentage change)
    df['momentum_1d'] = df['price'].pct_change(periods=1) * 100
    df['momentum_5d'] = df['price'].pct_change(periods=5) * 100
    df['momentum_10d'] = df['price'].pct_change(periods=10) * 100
    
    # Volatility (rolling standard deviation)
    df['volatility_10d'] = df['price'].rolling(window=10).std() / df['price'] * 100
    df['volatility_30d'] = df['price'].rolling(window=30).std() / df['price'] * 100
    
    return df
