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