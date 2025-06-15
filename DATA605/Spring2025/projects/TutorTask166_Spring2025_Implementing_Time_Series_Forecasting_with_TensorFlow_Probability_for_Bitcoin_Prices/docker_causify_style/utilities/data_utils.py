#!/usr/bin/env python3
"""
Data utility functions for the Bitcoin forecasting system.
Provides universal data handling functions for consistent operations across the application.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Union, Any, Optional

def safe_round(value: Any, decimals: int = 2) -> float:
    """
    Safely round a value regardless of its type (scalar, array, etc.).
    
    Args:
        value: Value to round (can be float, int, np.ndarray, etc.)
        decimals: Number of decimal places to round to
        
    Returns:
        Rounded float value
    """
    # Handle numpy arrays by taking the first element if it's a single-element array
    if isinstance(value, np.ndarray):
        if value.size == 1:
            # Convert single-element array to scalar
            value = value.item()
        else:
            # For multi-element arrays, just take the first element
            value = value[0]
    
    # Handle other numeric types
    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        # If we can't convert to float or round, return 0.0
        return 0.0

def ensure_tz_aware(dt: Union[datetime, pd.Timestamp]) -> datetime:
    """
    Ensure a datetime is timezone-aware by adding UTC timezone if it's naive.
    
    Args:
        dt: Datetime object or pandas Timestamp
        
    Returns:
        Timezone-aware datetime object with UTC timezone
    """
    if hasattr(dt, 'tzinfo') and dt.tzinfo is None:
        # For naive datetime, add UTC timezone
        return dt.replace(tzinfo=timezone.utc)
    return dt

def normalize_timestamps(df: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
    """
    Normalize timestamps in a DataFrame to ensure consistent timezone handling.
    
    Args:
        df: Pandas DataFrame with timestamp column
        timestamp_col: Name of the timestamp column
        
    Returns:
        DataFrame with normalized timestamps
    """
    if timestamp_col in df.columns:
        # Ensure all timestamps are timezone-aware (UTC)
        if pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            # Convert timezone-naive to timezone-aware (UTC)
            df[timestamp_col] = df[timestamp_col].dt.tz_localize(None).dt.tz_localize('UTC')
    return df

def compare_timestamps(timestamp1: Union[datetime, pd.Timestamp], 
                       timestamp2: Union[datetime, pd.Timestamp]) -> bool:
    """
    Safely compare two timestamps regardless of their timezone awareness.
    
    Args:
        timestamp1: First timestamp
        timestamp2: Second timestamp
        
    Returns:
        True if timestamp1 >= timestamp2, False otherwise
    """
    # Ensure both timestamps are timezone-aware
    t1 = ensure_tz_aware(timestamp1) if isinstance(timestamp1, (datetime, pd.Timestamp)) else timestamp1
    t2 = ensure_tz_aware(timestamp2) if isinstance(timestamp2, (datetime, pd.Timestamp)) else timestamp2
    
    # If one is a pandas Timestamp and the other is a datetime, convert both to datetime
    if isinstance(t1, pd.Timestamp) and isinstance(t2, datetime):
        t1 = t1.to_pydatetime()
    elif isinstance(t2, pd.Timestamp) and isinstance(t1, datetime):
        t2 = t2.to_pydatetime()
    
    return t1 >= t2

def filter_by_timestamp(df: pd.DataFrame, 
                       cutoff_time: Union[datetime, pd.Timestamp],
                       timestamp_col: str = 'timestamp') -> pd.DataFrame:
    """
    Filter DataFrame by timestamp, handling timezone differences safely.
    
    Args:
        df: Pandas DataFrame with timestamp column
        cutoff_time: Cutoff time for filtering
        timestamp_col: Name of the timestamp column
        
    Returns:
        Filtered DataFrame
    """
    if timestamp_col not in df.columns:
        return df
    
    # Normalize timestamps in the DataFrame
    df = normalize_timestamps(df, timestamp_col)
    
    # Ensure cutoff_time is timezone-aware
    cutoff_time = ensure_tz_aware(cutoff_time)
    
    # Convert cutoff_time to pandas Timestamp with UTC timezone if it's not already
    if not isinstance(cutoff_time, pd.Timestamp):
        cutoff_time = pd.Timestamp(cutoff_time).tz_convert('UTC')
    
    # Filter the DataFrame
    return df[df[timestamp_col] >= cutoff_time]

def format_price(price: Any, decimals: int = 2) -> str:
    """
    Format a price value for display, handling various input types.
    
    Args:
        price: Price value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted price string
    """
    rounded_price = safe_round(price, decimals)
    return f"{rounded_price:.{decimals}f}" 