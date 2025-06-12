"""
Utilize Celery to distribute across 3 key tasks for data ingestion/processing.

1. Celery documentation: https://docs.celeryq.dev/en/stable/getting-started/introduction.html

Task mapping:
1) process_trade_data
2) detect_anomaly
3) process_candle_data 

"""
# ------------------------------------------------------------------------------
# Import packages.
# -----------------------------------------------------------------------------
from celery import Celery, shared_task
from datetime import datetime
import logging
from collections import defaultdict, deque
import redis 
import traceback
import json
import numpy as np
r = redis.Redis(host='redis', port=6379, db=0)


# ------------------------------------------------------------------------------
# Import functions, define the app, logger, and checks
# -----------------------------------------------------------------------------

# Import functions.
from Falcon_functions import clean_trade, save_trade_to_cache, save_candle_to_timeseries, fetch_coinbase_candles

# Define the app and broker and backend.
app = Celery('Falcon_Celery_Tasks',
              broker='redis://redis:6379/0',
              backend='redis://redis:6379/0')

# Define logger for convenient prints.
logger = logging.getLogger(__name__)


# Health Check Task:
@app.task
def ping():
    return "pong"


# test stream global maxes
# Global count
MAX_MESSAGES = 1000
current_message_count = 0


# ------------------------------------------------------------------------------
# 1. process_trade_data
# ------------------------------------------------------------------------------
# Process data at ingest/endpoint by cleaning and storing.
@app.task
def process_trade_data(data, platform):
    global current_message_count
    if current_message_count >= MAX_MESSAGES:
        print("[celery] max mssg limit")
        return
    # Simulate processing
    print(f"[Celery] Processing {platform} trade {data.get('trade_id', 'no-id')}")
    current_message_count += 1
    try:
        logger.info("----- Celery process_trade_data -----")
        logger.info("Incoming data:", data)
        cleaned = clean_trade(data, platform)
        logger.info(f"Cleaned:", cleaned)  
        if cleaned: 
            #Save to redis for caching.
            save_trade_to_cache(cleaned, symbol=cleaned['symbol'], platform=platform)
            logger.info("Saved to cache.")
            #detect_anomaly.delay(cleaned)  # Chain to anomaly detection.
            #return chain(
                #process_trade_data.s(data, platform),
               # detect_anomaly.s()
           # )()
        return cleaned["core"] # Anomoly detection is expecting a dictionary.
    except Exception as e:
        logger.error(f"Failed to clean data: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------------------
# 2. detect_anomaly
# ------------------------------------------------------------------------------
# Idea: could ML be used here to detect anomalies or based on other data?
# Store last 500 prices per platform and detect anomolies based on rolling avg. 
price_history = defaultdict(lambda: deque(maxlen=500))

@app.task
def detect_anomaly(data):
    platform = data.get("platform", "unknown").lower()
    print(f"detect anomaly triggered for platform {platform}")
    price = float(data.get("price", 0))
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())

    # Update price history array based on platform.
    history = price_history[platform]
    history.append(price)

    # Handle when there isn't enough data to run.
    if len(history) < 30:
        # Not enough data yet
        logging.info(f"[{platform}] Warming up... {len(history)}/500 collected")
        return {"platform": platform, "price": price, "anomaly": False, "note": "warming_up"}

    # Compute rolling mean and std of prices.
    mean = np.mean(history)
    std = np.std(history)

    # Set the threshold for an "anomaly" in price.
    threshold = 2  # Detect spikes beyond 2 std deviations
    upper_bound = mean + threshold * std
    lower_bound = mean - threshold * std
    # Initialize as false. 
    is_anomaly = False
    # Check for anomoly.
    # Send alert if anomoly is detected and print the trade information. 
    if price > upper_bound or price < lower_bound:
        logging.warning(
            f"[ANOMALY] {platform} @ {timestamp} | Price: {price:.2f} | Mean: {mean:.2f} | Std: {std:.2f}"
        )
        is_anomaly = True
        # Save to a separate Redis key.
    # Send the anomoly to separate redis cache to use downstream.
    if is_anomaly:
        # Tag data before pushing to Redis.
        data["anomaly"] = True
        data["mean"] = mean
        data["std"] = std
        anomaly_key = f"anomalies:{platform}"
        r.lpush(anomaly_key, json.dumps(data))
        r.ltrim(anomaly_key, 0, 999)  # Keep only latest 1,000 anomalies
    # Return the whole trade information.
    return {
        "platform": platform,
        "price": price,
        "mean": mean,
        "std": std,
        "anomaly": is_anomaly
    }

# ------------------------------------------------------------------------------
# 3. process_ticker_data /NOT USED just an idea
# ------------------------------------------------------------------------------

# Celery task idea for price prediction relying on ticker data

@app.task
def process_ticker_data(msg, platform):
    # Store or preprocess ticker update for model training
    # PLACEHOLDER: print 
    print(f"[Ticker] Received for prediction: {data['price']} on {platform}")
    ...

# ------------------------------------------------------------------------------
# 3. process_candle_data
# -----------------------------------------------------------------------------

@app.task
def process_candle_data(candle):

#   candles = fetch_coinbase_candles("btc-usd", resolution="1d")
#   for c in candles:
#       # Convert timestamp to ms if needed
#       if c[0] < 1e12:
#           c[0] = int(c[0] * 1000)
#       save_candle_to_timeseries("coinbase", "btc_usd", "1d", c)

    try:
        platform = candle["platform"]
        symbol = candle["symbol"].lower().replace("-", "_")
        resolution = candle["resolution"]

        # Convert timestamp from ISO 8601 to ms if necessary
        ts = candle["timestamp"]
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                timestamp = int(ts.timestamp() * 1000)
            except Exception as parse_err:
                print(f" timestamp parse error {parse_err}")
                raise
        elif isinstance(ts, (int, float)):
            timestamp = int(ts)
        else:
            raise ValueError(f"unrecognized timestamp: {ts}")

        low = float(candle["low"])
        high = float(candle["high"])
        open_ = float(candle["open"])
        close = float(candle["close"])
        volume = float(candle["volume"])

        save_candle_to_timeseries(
            platform=platform,
            symbol=symbol,
            resolution=resolution,
            candle=[timestamp, low, high, open_, close, volume]
        )
        print(f"[process_candle_data] Stored candle for {platform}:{symbol} @ {timestamp}")
        print(f"[process_candle_data] Received: {candle}")
        return {"status": "ok"}

    except Exception as e:
        print(f"[process_candle_data ERROR] {e}")
        return {"status": "error", "message": str(e)}

