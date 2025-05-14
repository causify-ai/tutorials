from datetime import datetime
import pandas as pd

def to_iso8601(ts):
    # If already a string, just return
    if isinstance(ts, str):
        return ts
    # If it's a datetime, format it
    if hasattr(ts, 'isoformat'):
        return ts.isoformat(timespec='seconds').replace('+00:00', 'Z')
    # Fallback: convert to string
    return str(ts)

def format_timestamp(ts, use_t_separator=True):
    """
    Format timestamp consistently to ISO8601 format with T or space separator.
    
    Args:
        ts: timestamp as string, datetime, or numeric (epoch)
        use_t_separator: if True, use 'T' separator, otherwise use space
    
    Returns:
        str: formatted timestamp string in ISO8601 format
    """
    if isinstance(ts, str):
        # Parse string to datetime 
        ts = parse_timestamp(ts)
    elif isinstance(ts, (int, float)):
        # Convert epoch to datetime
        ts = datetime.utcfromtimestamp(ts)
        
    if ts is None:
        return None
        
    # Format with T separator or space based on preference
    format_string = "%Y-%m-%dT%H:%M:%S" if use_t_separator else "%Y-%m-%d %H:%M:%S"
    return ts.strftime(format_string)

def parse_timestamp(s):
    """Parse ISO8601 string or int/float epoch to datetime (UTC)."""
    if isinstance(s, (int, float)):
        return datetime.utcfromtimestamp(s)
    try:
        return pd.to_datetime(s, utc=True).to_pydatetime().replace(tzinfo=None)
    except Exception:
        # fallback: try as epoch
        try:
            return datetime.utcfromtimestamp(float(s))
        except Exception:
            return None 