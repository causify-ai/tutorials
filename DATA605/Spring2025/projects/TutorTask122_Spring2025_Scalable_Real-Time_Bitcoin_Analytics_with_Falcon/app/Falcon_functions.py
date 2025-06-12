'''functions
# ------------------------------------------------------------------------------
# Functions
# init_timeseries_keys initialize time series keys
# reset_timeseries_keys reset time series keys
# clean_trade clean and normalize trade data
# save_trade_to_cache cache trade in redis
# save_candle_to_timeseries store candle in redis time series
# fetch_coinbase_candles fetch historical candles from coinbase
# pull_and_store_coinbase_candles fetch and store coinbase candles
# ------------------------------------------------------------------------------

'''

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import redis 
import json
from datetime import datetime
import requests
from redistimeseries.client import Client as RedisTS

rts = RedisTS(host='redis', port=6379, db=1)


# ------------------------------------------------------------------------------
# Reset timeseries keys
# ------------------------------------------------------------------------------

def init_timeseries_keys(platform: str, symbol: str, resolution: str):
    base_key = f"ts:{platform}:{symbol}:{resolution}"
    metrics = ["open", "high", "low", "close", "volume"]
    for metric in metrics:
        key = f"{base_key}:{metric}"
        try:
            rts.create(key, duplicate_policy='last')
            print(f"[INIT] Created key: {key} with DUPLICATE_POLICY=last")
        except Exception as e:
            if "already exists" in str(e):
                print(f"[INIT] Key already exists: {key}")
            else:
                raise

def reset_timeseries_keys(platform: str, symbol: str, resolution: str):
    rts = RedisTS(host='redis', port=6379, db=1)
    base_key = f"ts:{platform}:{symbol}:{resolution}"
    metrics = ["open", "high", "low", "close", "volume"]

    # Delete old keys
    for metric in metrics:
        key = f"{base_key}:{metric}"
        rts.redis.delete(key)
        print(f"[RESET] Deleted key: {key}")

    # Recreate with correct policy
    for metric in metrics:
        key = f"{base_key}:{metric}"
        rts.create(key, duplicate_policy='last')
        print(f"[RESET] Re-created key: {key} with DUPLICATE_POLICY=last")

# ------------------------------------------------------------------------------
# Clean incoming data to have compatible labels 
# ------------------------------------------------------------------------------
def clean_trade(raw_data: dict, platform: str) -> dict:
    try:
        print(f"[clean_trade] Received raw data from {platform}: {raw_data}")
        if platform == "coinbase":
            core = {
                "platform": "coinbase",
                "symbol": raw_data.get("product_id", "BTC-USD"),
                "price": float(raw_data["price"]),
                "size": float(raw_data.get("last_size", 0)),
                "timestamp": raw_data["time"],
                "trade_id": raw_data.get("trade_id"),
            }
        elif platform == "binance":
            core = {
                "platform": "binance",
                "symbol": raw_data.get("s", "BTCUSDT"),
                "price": float(raw_data["p"]),
                "size": float(raw_data.get("q", 0)),
                "timestamp": datetime.utcfromtimestamp(raw_data["T"] / 1000).isoformat(),
                "trade_id": raw_data.get("t"),
            }
        else:
            print(f"[clean_trade] Unknown platform: {platform}")
            return None

        cleaned = {
            "core": core,
            "raw": raw_data  # Preserve full original payload.
        }
        print(f"[clean_trade] Cleaned data: {cleaned}")
        return cleaned


    except Exception as e:
        print(f"[clean_trade] Error: {e}")
        return None
# ------------------------------------------------------------------------------
# Initialize Redis connection
# -----------------------------------------------------------------------------
r = redis.Redis(host='localhost', port=6379, db=0)

def save_trade_to_cache(trade: dict, symbol: str = "BTCUSDT", platform: str = "binance", max_trades: int = 5000):
    """
    Save a cleaned trade (including 'core' and 'raw') to Redis list with length cap.

    Args:
        trade (dict): Dictionary with 'core' and optionally 'raw' trade data.
        symbol (str): Trading symbol like 'BTCUSDT'.
        platform (str): 'binance' or 'coinbase'.
        max_trades (int): Max number of trades to keep in Redis.
    """
    key = f"trades:{platform}:{symbol.lower()}"
    try:
        # Save to rolling list
        print(f"[save_trade_to_cache] Saving trade to key: {key}")
        r.lpush(key, json.dumps(trade))
        r.ltrim(key, 0, max_trades - 1)

        # Also store the most recent trade for fast access
        latest_key = f"{key}:latest"
        r.set(latest_key, json.dumps(trade))
        print(f"[save_trade_to_cache] Successfully cached trade for {platform}:{symbol}")

    except Exception as e:
        print(f"[Redis Error] Could not save trade: {e}")
# ------------------------------------------------------------------------------
# Initialize Redis timeseries client for LSTM modeling
# -----------------------------------------------------------------------------
# Saves one candle to RedisTimeSeries.
rts = RedisTS(host='redis', port=6379, db = 1)

def save_candle_to_timeseries(platform: str, symbol: str, resolution: str, candle: list):
    timestamp = candle[0]
    low, high, open_, close, volume = candle[1:]

    base_key = f"ts:{platform}:{symbol}:{resolution}"
    try:
        print(f"[RedisTS] Storing OHLCV for key prefix: {base_key} @ {timestamp}")
        for metric, value in zip(["open", "high", "low", "close", "volume"], [open_, high, low, close, volume]):
            key = f"{base_key}:{metric}"
            rts.add(key, timestamp, value, duplicate_policy="last")
        print(f"[RedisTS] Stored OHLCV @ {timestamp} for {symbol} ({resolution})")
    except Exception as e:
        print(f"[RedisTS Error] Could not store candle: {e}")


# ------------------------------------------------------------------------------
# Fetch Coinbase Candles for LSTM training/validate/test
# -----------------------------------------------------------------------------
# Fetches and returns a list of raw OHLCV candles.
RESOLUTION_MAP = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "1d": 86400
}

def fetch_coinbase_candles(symbol="BTC-USD", resolution="1m", start=None, end=None, limit=300):
    """
    Fetch historical candles (OHLCV) from Coinbase.

    Args:
        symbol (str): e.g., "BTC-USD"
        resolution (str): one of {"1m", "5m", "15m", "1h", "1d"}
        start (str): ISO8601 time
        end (str): ISO8601 time
        limit (int): Ignored by Coinbase but useful for downstream slicing

    Returns:
        List of [time, low, high, open, close, volume]
    """
    if resolution not in RESOLUTION_MAP:
        raise ValueError(f"Unsupported resolution: {resolution}")
    granularity = RESOLUTION_MAP[resolution]

    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    print("coinbase url", url)
    params = {
        "granularity": granularity,
    }

    if start:
        params["start"] = start
    if end:
        params["end"] = end

    headers = {
        "User-Agent": "Falcon-Crypto-Client"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"[Coinbase API Error] {response.status_code}: {response.text}")
        return []

    data = response.json()

    candles = []
    for row in sorted(data, key=lambda x: x[0]):
        candles.append([
           row[0],  # timestamp in seconds
        row[1],  # low
        row[2],  # high
        row[3],  # open
        row[4],  # close
        row[5]   # volume 
        ])
    print(f"[fetch_coinbase_candles] Returning {len(candles)} candles")
    return candles


# ------------------------------------------------------------------------------
# Pull and store candles
# -----------------------------------------------------------------------------
# Glue between previous Redis cache and fetch 
# Calls fetch and then posts to Falcon
def pull_and_store_coinbase_candles(symbol="BTC-USD", resolution="1m", start=None, end=None):
    """
    Fetch OHLCV candles from Coinbase and push them to RedisTimeSeries.
    """
    candles = fetch_coinbase_candles(symbol=symbol, resolution=resolution, start=start, end=end)
    for candle in candles:
        save_candle_to_timeseries("coinbase", symbol.lower().replace("-", "_"), resolution, candle)
