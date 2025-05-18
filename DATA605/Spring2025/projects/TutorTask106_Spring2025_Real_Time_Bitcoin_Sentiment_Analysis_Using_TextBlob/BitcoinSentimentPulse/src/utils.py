import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple

def format_large_number(num: float) -> str:
    """
    Format large numbers for display (e.g., 1234.56 -> 1,234.56)
    
    Args:
        num (float): Number to format
        
    Returns:
        str: Formatted number string
    """
    return f"{num:,.2f}"

def get_color_from_value(value: float, threshold_positive: float = 0, threshold_negative: float = 0) -> str:
    """
    Return a color string based on the value.
    
    Args:
        value (float): The value to check
        threshold_positive (float): Threshold for positive values
        threshold_negative (float): Threshold for negative values
        
    Returns:
        str: Color string
    """
    if value > threshold_positive:
        return "green"
    elif value < threshold_negative:
        return "red"
    else:
        return "gray"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value (float): Original value
        new_value (float): New value
        
    Returns:
        float: Percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add time-based features to the DataFrame for time series analysis.
    
    Args:
        df (pd.DataFrame): DataFrame with datetime index
        
    Returns:
        pd.DataFrame: DataFrame with added time features
    """
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Extract datetime features
    result['day_of_week'] = result.index.dayofweek
    result['day_of_month'] = result.index.day
    result['week_of_year'] = result.index.isocalendar().week
    result['month'] = result.index.month
    result['quarter'] = result.index.quarter
    result['year'] = result.index.year
    
    # Create cyclical features for day_of_week
    result['day_of_week_sin'] = np.sin(2 * np.pi * result['day_of_week'] / 7)
    result['day_of_week_cos'] = np.cos(2 * np.pi * result['day_of_week'] / 7)
    
    # Create cyclical features for month
    result['month_sin'] = np.sin(2 * np.pi * result['month'] / 12)
    result['month_cos'] = np.cos(2 * np.pi * result['month'] / 12)
    
    return result

def detect_outliers(df: pd.DataFrame, column: str, window: int = 20, threshold: float = 3.0) -> pd.Series:
    """
    Detect outliers in time series data using the rolling z-score method.
    
    Args:
        df (pd.DataFrame): DataFrame with time series data
        column (str): Column name to check for outliers
        window (int): Rolling window size
        threshold (float): Z-score threshold for outlier detection
        
    Returns:
        pd.Series: Boolean series indicating outlier points
    """
    # Calculate rolling mean and standard deviation
    rolling_mean = df[column].rolling(window=window, center=True).mean()
    rolling_std = df[column].rolling(window=window, center=True).std()
    
    # Calculate z-scores
    z_scores = (df[column] - rolling_mean) / rolling_std
    
    # Identify outliers where z-score exceeds threshold
    outliers = abs(z_scores) > threshold
    
    return outliers
