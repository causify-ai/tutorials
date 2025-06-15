"""


Functions:
-----------------
1. train_lstm_and_save
Fetches candle data from Redis, prepares sequences, trains an LSTM, and saves
    the model to models/{symbol}_{resolution}.h5.
used by train task in Falcon_Celery_Tasks_lstm.py
# Trains an LSTM model using candle data from Redis and saves the model to disk.
# Called only by the LSTM Celery worker (`train` task).
-----------------
2. load_lstm_and_predict
Loads a pre-trained LSTM model from disk, fetches the latest sequence from Redis, 
    and returns a single predicted price.
used by predict in Falcon_Celery_Tasks_lstm.py.
# Loads a saved LSTM model from disk and predicts the next price using recent Redis data.
# Called by the LSTM Celery worker (`predict` task).
--------------
3. train_lstm_from_redis()
# Internal helper function to train an LSTM model on data pulled from Redis.
# Returns an in-memory Keras model object.
# Called only by `train_lstm_and_save(...)`.
. predict_next_price()


"""
# ------------------------------------------------------------------------------
# Import packages.
# -----------------------------------------------------------------------------
from Falcon_functions import fetch_coinbase_candles
import requests 
from redistimeseries.client import Client as RedisTS
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
import os
import json
# ------------------------------------------------------------------------------
# BACKFILL CANDLES
# -----------------------------------------------------------------------------


def backfill_candles_to_falcon(api_url, symbol="BTC-USD", start=None, end=None, resolution="1m", granularity=60):
    candles = fetch_coinbase_candles(symbol=symbol,
                                    resolution=resolution,
                                    start=start,
                                    end=end)
    for candle in candles:
        payload = {
            "symbol": symbol,
            "timestamp": candle[0],
            "open": candle[3],
            "high": candle[2],
            "low": candle[1],
            "close": candle[4],
            "volume": candle[5],
            "resolution": resolution
        }
        r = requests.post(f"{api_url}/ingest/kline/coinbase", json=payload)
        print(f"{r.status_code}: {r.text}")

# ------------------------------------------------------------------------------
# Predict Next Price
# -----------------------------------------------------------------------------

def predict_next_price(model, symbol="btc_usd", resolution="1m", seq_len=10, model_id=1):
    rts = RedisTS(host="redis", port=6379, db=model_id)
    key = f"ts:coinbase:{symbol}:{resolution}:close"
    #raw = rts.range(key, 0, -1)#orig
    raw = rts.range(key, '-', '+')
    series = [float(x[1]) for x in raw[-seq_len:]]
    
    if len(series) < seq_len:
        raise ValueError("Not enough data for prediction")

    X = np.array(series).reshape(1, seq_len, 1)
    return model.predict(X)[0][0]

# --------------------------------
# IMPLEMENT live stream to notebook
# ---------------------------------
def send_trade(platform, trade_data):
    url = f"http://localhost:8000/ingest/{platform}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(trade_data))
    return response.status_code



# ------------------------------------------------------------------------------
# HELPER to Normalize the data
# -----------------------------------------------------------------------------
def normalize_series(series):
    min_val = np.min(series)
    max_val = np.max(series)
    normalized = (series - min_val) / (max_val - min_val)
    return normalized, min_val, max_val

def denormalize_value(norm_val, min_val, max_val):
    return norm_val * (max_val - min_val) + min_val

# ------------------------------------------------------------------------------
# LSTM
# -----------------------------------------------------------------------------

def train_lstm_from_redis(model_name="", symbol="btc_usd", resolution="1d", seq_len=10, model_id=1):
    rts = RedisTS(host="redis", port=6379, db=model_id)
    key = f"ts:coinbase:{symbol}:{resolution}:close"
    raw = rts.range(key, '-', '+')
    series = np.array([float(x[1]) for x in raw])
    print("series lenght", series)
    print("sequence length", seq_len)

    if len(series) < seq_len + 1:
        raise ValueError(f"Not enough data to train. {len(series)} {seq_len}")

    # Use helper
    norm_series, min_val, max_val = normalize_series(series)

    # Save normalization params
    os.makedirs("models", exist_ok=True)
    with open(f"models/{model_name}_{symbol}_{resolution}_norm.json", "w") as f:
        json.dump({"min": min_val, "max": max_val}, f)

    # Create sequences
    X, y = [], []
    for i in range(len(norm_series) - seq_len):
        X.append(norm_series[i:i+seq_len])
        y.append(norm_series[i+seq_len])
    X = np.array(X).reshape(-1, seq_len, 1)
    y = np.array(y)

    model = Sequential([
        LSTM(32, input_shape=(seq_len, 1)),
        Dense(1)
    ])
    model.compile(loss="mse", optimizer="adam")
    model.fit(X, y, epochs=5, verbose=1)

    return [model, min_val, max_val]

# ------------------------------------------------------------------------------
# LSTM
# -----------------------------------------------------------------------------
def train_lstm_and_save(model_name="", symbol="btc_usd", resolution="1m", seq_len=10, model_id=1):
    packer = train_lstm_from_redis(model_name, symbol, resolution, seq_len, model_id=model_id)
    model=packer[0]
    min_val=packer[1]
    max_val=packer[2]
    path = f"models/{model_name}_{symbol}_{resolution}.h5"
    os.makedirs("models", exist_ok=True)
    model.save(path)
    with open(f"models/{model_name}_{symbol}_{resolution}_norm.json", "w") as f:
        json.dump({"min": min_val, "max": max_val}, f)
    print(f"[train_lstm_and_save] Saved model to {path}")
    return path

# ------------------------------------------------------------------------------
# LSTM n steps 
# -----------------------------------------------------------------------------
def load_lstm_and_predict(model_name="", symbol="btc_usd", resolution="1d", seq_len=10, model_id=1):
    model_path = f"models/{model_name}_{symbol}_{resolution}.h5"
    norm_path = f"models/{model_name}_{symbol}_{resolution}_norm.json"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found at {model_path}")
    if not os.path.exists(norm_path):
        raise FileNotFoundError(f"No norm file found at {norm_path}")

    model = load_model(model_path)
    with open(norm_path, "r") as f:
        norm_params = json.load(f)
        min_val = norm_params["min"]
        max_val = norm_params["max"]

    rts = RedisTS(host="redis", port=6379, db=model_id)
    key = f"ts:coinbase:{symbol}:{resolution}:close"
    raw = rts.range(key, '-', '+')
    series = np.array([float(x[1]) for x in raw])

    if len(series) < seq_len:
        raise ValueError("Not enough data to predict.")

    norm_input = (series[-seq_len:] - min_val) / (max_val - min_val)
    X = norm_input.reshape(1, seq_len, 1)

    norm_pred = model.predict(X)[0][0]
    pred = denormalize_value(norm_pred, min_val, max_val)

    print(f"[load_lstm_and_predict] Normalized prediction: {norm_pred}, Actual prediction: {pred}")
    return pred
