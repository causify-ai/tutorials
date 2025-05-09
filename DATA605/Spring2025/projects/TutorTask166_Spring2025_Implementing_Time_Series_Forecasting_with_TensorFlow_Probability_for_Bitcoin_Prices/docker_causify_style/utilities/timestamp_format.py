from datetime import datetime
import pandas as pd

def to_iso8601(dt):
    """Convert datetime, int, or float to ISO8601 string (UTC, no microseconds)."""
    if isinstance(dt, (int, float)):
        dt = datetime.utcfromtimestamp(dt)
    elif isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()
    return dt.replace(microsecond=0).isoformat()

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