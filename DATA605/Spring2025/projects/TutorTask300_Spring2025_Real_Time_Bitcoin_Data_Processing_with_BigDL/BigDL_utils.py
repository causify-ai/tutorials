"""
template_utils.py  ·  Utilities for the BigDL-Bitcoin tutorial
────────────────────────────────────────────────────────────────
Keep notebooks clean by importing these helpers instead of
re-implementing logic in multiple places.

Functions
---------
get_spark_session()           -> SparkSession
fetch_bitcoin_prices()        -> Spark DataFrame (timestamp, price)
process_bitcoin_data()        -> cleaned Spark DataFrame
transform_bitcoin_data()      -> engineered Spark DataFrame
prepare_sequences()           -> np.ndarray X,  y
to_samples()                  -> list[bigdl.dllib.utils.common.Sample]
build_lstm_model()            -> bigdl.dllib.nn.layer.Sequential
train_bigdl_model()           -> trained model
rmse(), mape()                -> float metrics
plot_forecast(), plot_residuals()

All routines are **pure-Python** except the Spark / BigDL calls so they
can be unit-tested without a cluster by passing stub data.
"""

from __future__ import annotations

import logging
import math
import os
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession, Window, DataFrame
from pyspark.sql.functions import (
    avg,
    col,
    from_unixtime,
    lag,
)
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from bigdl.dllib.nn.criterion import MSECriterion
from bigdl.dllib.nn.layer import (
    LSTM,
    Linear,
    Recurrent,
    Reshape,
    Select,
    Sequential,
    TimeDistributed,
)
from bigdl.dllib.optim.optimizer import Adam, MaxEpoch, Optimizer
from bigdl.dllib.utils.common import Sample, init_engine

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Spark helpers
# ---------------------------------------------------------------------


def get_spark_session(app_name: str = "BigDLBitcoin") -> SparkSession:
    """Return (and cache) a local Spark 3 session."""
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )


# ---------------------------------------------------------------------
# ETL helpers – fetch → clean → feature-engineer
# ---------------------------------------------------------------------


def fetch_bitcoin_prices(
    api_url: str = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
    vs_currency: str = "usd",
    days: int = 1,
) -> DataFrame:
    """Download recent BTC-USD data (minute resolution) from CoinGecko."""
    import requests  # local import to keep the global dependency list short

    _LOG.info("Downloading %s days of BTC-USD prices from CoinGecko", days)
    resp = requests.get(api_url, params={"vs_currency": vs_currency, "days": days}, timeout=30)
    resp.raise_for_status()
    prices = resp.json().get("prices", [])  # [[ts_ms, price], …]

    spark = get_spark_session()
    return spark.createDataFrame([{"timestamp": ts, "price": p} for ts, p in prices])


def process_bitcoin_data(df: DataFrame) -> DataFrame:
    """Cast types and sort."""
    spark = df.sparkSession
    with_ts = df.withColumn("time", from_unixtime(col("timestamp") / 1000).cast("timestamp"))
    cleaned = (
        with_ts.select("time", col("price").cast("double"))
        .orderBy("time")
        .cache()
    )
    _LOG.debug("Cleaned DF rows = %s", cleaned.count())
    return cleaned


def transform_bitcoin_data(df: DataFrame) -> DataFrame:
    """Add 60-minute rolling mean and % change feature columns."""
    w_range = Window.orderBy("time").rangeBetween(-60 * 60, 0)
    w_order = Window.orderBy("time")

    engineered = (
        df.withColumn("rolling_avg_1h", avg("price").over(w_range))
        .withColumn("prev_price", lag("price", 1).over(w_order))
        .withColumn(
            "pct_change", (col("price") - col("prev_price")) / col("prev_price") * 100
        )
        .drop("prev_price")
    )
    return engineered


# ---------------------------------------------------------------------
# Sequencing, scaling, Samples
# ---------------------------------------------------------------------


def prepare_sequences(prices: List[float], time_steps: int) -> Tuple[np.ndarray, np.ndarray]:
    """Convert a 1-D price list into sliding windows X, y."""
    X, y = [], []
    for i in range(len(prices) - time_steps):
        X.append(prices[i : i + time_steps])
        y.append(prices[i + time_steps])
    return np.asarray(X, dtype=np.float32), np.asarray(y, dtype=np.float32)


def to_samples(X: np.ndarray, y: np.ndarray) -> List[Sample]:
    """Wrap numpy arrays into BigDL Sample objects."""
    samples = []
    for features, label in zip(X, y, strict=True):
        samples.append(Sample.from_ndarray(features.reshape(features.shape[0], 1), [label]))
    return samples


# ---------------------------------------------------------------------
# Model / training
# ---------------------------------------------------------------------


def build_lstm_model(time_steps: int, hidden_size: int) -> Sequential:
    """Create a minimal [time_steps → 1] LSTM network."""
    model = Sequential()
    model.add(Reshape([time_steps, 1]))
    model.add(Recurrent().add(LSTM(input_size=1, hidden_size=hidden_size)))
    model.add(TimeDistributed(Linear(hidden_size, 1)))
    model.add(Select(2, -1))  # keep the last timestep only
    return model


def train_bigdl_model(
    df: DataFrame,
    time_steps: int = 20,
    hidden_size: int = 64,
    epochs: int = 5,
    batch_size: int = 32,
) -> Tuple[Sequential, MinMaxScaler]:
    """
    End-to-end: scale → window → Sample → train → return (model, scaler).
    """
    init_engine()

    spark = df.sparkSession
    prices = df.select("price").rdd.map(lambda r: r[0]).collect()

    scaler = MinMaxScaler()
    prices_scaled = scaler.fit_transform(np.asarray(prices).reshape(-1, 1)).flatten()

    X, y = prepare_sequences(prices_scaled, time_steps)
    samples = spark.sparkContext.parallelize(to_samples(X, y))

    model = build_lstm_model(time_steps, hidden_size)

    optimizer = Optimizer(
        model=model,
        training_rdd=samples,
        criterion=MSECriterion(),
        optim_method=Adam(),
        end_trigger=MaxEpoch(epochs),
        batch_size=batch_size,
    )
    trained = optimizer.optimize()
    return trained, scaler


# ---------------------------------------------------------------------
# Forecasting utils
# ---------------------------------------------------------------------


def predict_autoregressive(
    model: Sequential,
    scaler: MinMaxScaler,
    recent_unscaled: List[float],
    future_steps: int = 10,
) -> List[float]:
    """Iteratively forecast `future_steps` points using the last window."""
    window_scaled = scaler.transform(np.asarray(recent_unscaled).reshape(-1, 1)).flatten().tolist()
    preds_real = []

    for _ in range(future_steps):
        arr = np.asarray(window_scaled, dtype=np.float32).reshape((1, len(window_scaled), 1))
        pred_scaled = float(model.predict(arr).squeeze())
        pred_real = scaler.inverse_transform([[pred_scaled]])[0][0]

        preds_real.append(pred_real)
        window_scaled = window_scaled[1:] + [pred_scaled]  # slide window

    return preds_real


# ---------------------------------------------------------------------
# Metrics & visuals
# ---------------------------------------------------------------------


def rmse(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Root‐Mean‐Square-Error."""
    return math.sqrt(mean_squared_error(actual, forecast))


def mape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Mean-Absolute-Percentage-Error (0-100 %)."""
    return mean_absolute_percentage_error(actual, forecast) * 100


def plot_forecast(
    df: DataFrame,
    forecast: List[float],
    freq: str = "H",
    title: str = "BTC-USD – Actual vs. BigDL Forecast",
) -> None:
    """Line plot of actual history + forecast horizon."""
    pdf = df.toPandas()
    hist_times, hist_prices = pdf["time"], pdf["price"]

    future_times = pd.date_range(hist_times.iloc[-1], periods=len(forecast) + 1, freq=freq)[1:]

    plt.figure(figsize=(11, 6))
    plt.plot(hist_times, hist_prices, label="Actual", linewidth=2)
    plt.plot(future_times, forecast, label="Forecast", linewidth=2)
    plt.title(title)
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_residuals(actual: np.ndarray, forecast: np.ndarray) -> None:
    """Histogram + density of residuals."""
    residuals = actual - forecast
    plt.figure(figsize=(8, 4))
    plt.hist(residuals, bins=40, alpha=0.7, density=True)
    plt.title("Forecast Residual Distribution")
    plt.xlabel("Residual (USD)")
    plt.ylabel("Density")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------
# Convenience: ensure output dir exists
# ---------------------------------------------------------------------


def ensure_dir(path: os.PathLike | str) -> Path:
    """Create *path* if missing and return as `Path`."""
    p = Path(path)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    return p
