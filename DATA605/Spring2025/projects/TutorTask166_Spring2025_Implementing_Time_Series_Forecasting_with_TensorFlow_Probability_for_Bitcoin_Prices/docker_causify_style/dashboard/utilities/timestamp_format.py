from datetime import datetime, timezone
import pandas as pd

# Define constants for consistent timestamp handling
UTC_TIMEZONE = timezone.utc
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"  # ISO-8601 format without timezone
DEFAULT_TIMESTAMP_FORMAT_TZ = "%Y-%m-%dT%H:%M:%S UTC"  # ISO-8601 format with timezone (simplified)

def to_iso8601(ts, include_timezone=True):
    """
    Convert timestamp to ISO-8601 format string.
    
    Args:
        ts: timestamp as string, datetime, or numeric (epoch)
        include_timezone: whether to include timezone information (default: True)
    
    Returns:
        str: formatted timestamp string in ISO-8601 format
    """
    # Parse timestamp to normalized datetime
    ts_dt = normalize_timestamp(ts)
    
    if ts_dt is None:
        return None
    
    # Format with timezone info based on preference
    if include_timezone:
        # Use simplified UTC format for consistency with web app
        return ts_dt.strftime(DEFAULT_TIMESTAMP_FORMAT) + " UTC"
    else:
        # Use format without timezone
        return ts_dt.strftime(DEFAULT_TIMESTAMP_FORMAT)

def format_timestamp(ts, use_t_separator=True, include_timezone=False):
    """
    Format timestamp consistently to ISO8601 format with T or space separator.
    
    Args:
        ts: timestamp as string, datetime, or numeric (epoch)
        use_t_separator: if True, use 'T' separator, otherwise use space
        include_timezone: whether to include timezone information (default: False)
    
    Returns:
        str: formatted timestamp string in ISO8601 format
    """
    # Parse timestamp to normalized datetime
    ts_dt = normalize_timestamp(ts)
    
    if ts_dt is None:
        return None
    
    # Format with T separator or space based on preference
    format_string = "%Y-%m-%dT%H:%M:%S" if use_t_separator else "%Y-%m-%d %H:%M:%S"
    
    # Add timezone info if requested
    if include_timezone:
        # Use simplified UTC format for consistency with web app
        return ts_dt.strftime(format_string) + " UTC"
    else:
        # If we don't want timezone but have one, strip it
        if ts_dt.tzinfo is not None:
            ts_dt = ts_dt.replace(tzinfo=None)
            
        return ts_dt.strftime(format_string)

def parse_timestamp(s, assume_utc=True):
    """
    Parse ISO8601 string or int/float epoch to datetime.
    
    Args:
        s: timestamp as string, datetime, or numeric (epoch)
        assume_utc: whether to assume UTC timezone for timestamps without timezone info
        
    Returns:
        datetime: parsed datetime object, always normalized (timezone-naive)
    """
    # Return directly if already a datetime
    if isinstance(s, datetime):
        return normalize_timestamp(s)
        
    # Handle numeric timestamps (epoch)
    if isinstance(s, (int, float)):
        dt = datetime.fromtimestamp(s, tz=UTC_TIMEZONE)
        return dt.replace(tzinfo=None)  # Return as timezone-naive
    
    # Handle string timestamps
    try:
        # Handle UTC suffix in string format
        if isinstance(s, str) and s.endswith(" UTC"):
            s = s.replace(" UTC", "")
        
        # Use pandas for flexible parsing
        dt = pd.to_datetime(s, utc=assume_utc)
        
        # Convert to Python datetime and normalize
        if hasattr(dt, 'to_pydatetime'):
            dt = dt.to_pydatetime()
        
        # Return as timezone-naive
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
            
        return dt
    except Exception:
        # fallback: try as epoch
        try:
            return datetime.fromtimestamp(float(s), tz=UTC_TIMEZONE).replace(tzinfo=None)
        except Exception:
            return None

def normalize_timestamp(ts):
    """
    Normalize timestamp to a consistent format (always timezone-naive).
    
    Args:
        ts: timestamp as string, datetime, or numeric (epoch)
        
    Returns:
        datetime: normalized datetime object (timezone-naive)
    """
    # Return None for None input
    if ts is None:
        return None
        
    # Already datetime - just normalize the timezone
    if isinstance(ts, datetime):
        # If has timezone, convert to UTC then strip timezone
        if ts.tzinfo is not None:
            ts = ts.astimezone(UTC_TIMEZONE)
            return ts.replace(tzinfo=None)
        # Already timezone-naive
        return ts
        
    # Use parse_timestamp for all other cases
    return parse_timestamp(ts)

def compare_timestamps(ts1, ts2):
    """
    Compare two timestamps safely, regardless of their format or timezone.
    
    Args:
        ts1: first timestamp (string, datetime, or numeric)
        ts2: second timestamp (string, datetime, or numeric)
        
    Returns:
        int: -1 if ts1 < ts2, 0 if ts1 == ts2, 1 if ts1 > ts2
    """
    # Normalize both timestamps
    dt1 = normalize_timestamp(ts1)
    dt2 = normalize_timestamp(ts2)
    
    # Handle None values
    if dt1 is None and dt2 is None:
        return 0
    if dt1 is None:
        return -1
    if dt2 is None:
        return 1
        
    # Compare normalized datetimes
    if dt1 < dt2:
        return -1
    elif dt1 > dt2:
        return 1
    else:
        return 0

def ensure_consistent_formats(df, timestamp_column='timestamp', include_timezone=True):
    """
    Ensure all timestamps in a dataframe have consistent format.
    
    Args:
        df: pandas DataFrame containing timestamps
        timestamp_column: name of the timestamp column
        include_timezone: whether to include timezone in the output format
        
    Returns:
        pandas.DataFrame: DataFrame with normalized timestamps
    """
    if df is None or df.empty or timestamp_column not in df.columns:
        return df
        
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Convert timestamps to datetime objects
    df[timestamp_column] = pd.to_datetime(df[timestamp_column], errors='coerce', utc=True)
    
    # Convert datetime objects to consistent string format if needed
    if include_timezone:
        # With timezone - use simplified UTC format for consistency
        df[timestamp_column] = df[timestamp_column].dt.strftime(DEFAULT_TIMESTAMP_FORMAT) + " UTC"
    else:
        # Without timezone
        # Convert to UTC, then remove timezone, then format
        df[timestamp_column] = df[timestamp_column].dt.tz_localize(None).dt.strftime(DEFAULT_TIMESTAMP_FORMAT)
        
    return df 