"""
btc_trade_utils.py

Helper functions for Bitcoin trade processing.

- Provides utilities like OHLC computation and time bucketing.
- All heavy task logic is moved to btc_trade_API.py.
"""

from datetime import datetime
from collections import defaultdict
import logging
from huey import RedisHuey

# -----------------------------------------------------------------------------
# Setup Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Huey Instance
# -----------------------------------------------------------------------------

huey = RedisHuey('btc-trade', host='redis', port=6379)

# -----------------------------------------------------------------------------
# OHLC Aggregation Buckets
# -----------------------------------------------------------------------------

ohlc_1min = defaultdict(list)
ohlc_5min = defaultdict(list)

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_bucket(timestamp: str, interval: str = '1min') -> datetime:
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if interval == '1min':
        return dt.replace(second=0, microsecond=0)
    elif interval == '5min':
        rounded_minute = dt.minute - (dt.minute % 5)
        return dt.replace(minute=rounded_minute, second=0, microsecond=0)
    return dt


def compute_ohlc(prices: list) -> dict:
    if not prices:
        return {"open": None, "high": None, "low": None, "close": None}
    
    return {
        "open": prices[0],
        "high": max(prices),
        "low": min(prices),
        "close": prices[-1]
    }
