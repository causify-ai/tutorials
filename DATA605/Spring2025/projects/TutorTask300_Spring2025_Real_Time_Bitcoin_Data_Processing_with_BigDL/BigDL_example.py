import os
from datetime import timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# ------------------------- BigDL imports -------------------------
from bigdl.dllib.utils.common import init_engine, Sample
from bigdl.dllib.nn.layer import (
    Sequential,
    Reshape,
    Recurrent,
    LSTM,
    TimeDistributed,
    Linear,
    Select,
)
from bigdl.dllib.nn.criterion import MSECriterion
from bigdl.dllib.optim.optimizer import Optimizer, Adam, MaxEpoch

# ------------------------- Project utilities ---------------------
from BigDL_API import (
    get_spark_session,
    fetch_bitcoin_prices,
    process_bitcoin_data,
    transform_bitcoin_data,
    load_bitcoin_data,
)

# -----------------------------------------------------------------
# 1. ETL PIPELINE
# -----------------------------------------------------------------

def etl_pipeline(days: int, output_path: str):
    """End‑to‑end ingestion → cleaning → feature engineering → load."""
    spark = get_spark_session()

    raw_df = fetch_bitcoin_prices(days=days)
    clean_df = process_bitcoin_data(raw_df)
    transformed_df = transform_bitcoin_data(clean_df)

    load_bitcoin_data(transformed_df, output_path)
    return transformed_df


# -----------------------------------------------------------------
# 2. DATA PREP HELPERS
# -----------------------------------------------------------------

def _prepare_sequences(series: np.ndarray, time_steps: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return inputs / targets windows for supervised learning."""
    X, y = [], []
    for i in range(len(series) - time_steps):
        X.append(series[i : i + time_steps])
        y.append(series[i + time_steps])
    return np.asarray(X, dtype=np.float32), np.asarray(y, dtype=np.float32)


# -----------------------------------------------------------------
# 3. MODEL TRAINING
# -----------------------------------------------------------------

def train_rnn_model(
    df,
    time_steps: int = 20,
    hidden_size: int = 64,
    epochs: int = 5,
):
    """Train a simple LSTM on closing prices using BigDL DLlib."""

    # --- Initialise BigDL (must be called exactly once) ---
    init_engine()
    spark = get_spark_session()

    # --- Extract closing prices & scale to 0‑1 range ---
    prices = np.asarray(df.select("price").rdd.map(lambda r: r[0]).collect()).reshape(-1, 1)
    scaler = MinMaxScaler()
    prices_scaled = scaler.fit_transform(prices).flatten()

    # --- Window into sequences ---
    X, y = _prepare_sequences(prices_scaled, time_steps)

    # --- Define network ---
    model = Sequential()
    model.add(Reshape([time_steps, 1]))
    model.add(Recurrent().add(LSTM(input_size=1, hidden_size=hidden_size)))  # last output only
    model.add(TimeDistributed(Linear(hidden_size, 1)))
    model.add(Select(2, -1))  # take last timestep of sequence

    # --- Convert to RDD[Sample] ---
    samples = [Sample.from_ndarray(X[i].reshape(time_steps, 1), np.array([y[i]])) for i in range(len(y))]
    training_rdd = spark.sparkContext.parallelize(samples)

    # --- Optimiser config ---
    optimizer = Optimizer(
        model=model,
        training_rdd=training_rdd,
        criterion=MSECriterion(),
        optim_method=Adam(),
        batch_size=32,
        end_trigger=MaxEpoch(epochs),
    )
    trained_model = optimizer.optimize()
    return trained_model, scaler


# -----------------------------------------------------------------
# 4. FORECASTING
# -----------------------------------------------------------------

def predict_future(
    model,
    scaler: MinMaxScaler,
    recent_prices: List[float],
    future_steps: int = 10,
):
    """Autoregressively forecast the next *n* steps (in raw price units)."""
    # Normalise the most recent window
    seq_scaled = scaler.transform(np.asarray(recent_prices).reshape(-1, 1)).flatten().tolist()
    preds_real: List[float] = []

    for _ in range(future_steps):
        x_in = np.asarray(seq_scaled, dtype=np.float32).reshape(1, len(seq_scaled), 1)
        pred_scaled = float(model.predict(x_in).squeeze())
        pred_real = scaler.inverse_transform([[pred_scaled]])[0, 0]

        preds_real.append(pred_real)
        seq_scaled = seq_scaled[1:] + [pred_scaled]  # slide window

    return preds_real


# -----------------------------------------------------------------
# 5. METRICS & VISUALS
# -----------------------------------------------------------------

def compute_metrics(actual: np.ndarray, forecast: np.ndarray):
    rmse = np.sqrt(mean_squared_error(actual, forecast))
    mape = mean_absolute_percentage_error(actual, forecast) * 100
    return rmse, mape


def plot_forecast(times: pd.Series, actual: pd.Series, future_ts: pd.DatetimeIndex, forecast: List[float]):
    plt.figure(figsize=(10, 6))
    plt.plot(times, actual, label="Actual", linewidth=2)
    plt.plot(future_ts, forecast, label="Forecast", linestyle="--", linewidth=2)
    plt.title("BTC‑USD – Actual vs. BigDL Forecast")
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_residuals(actual: np.ndarray, forecast: np.ndarray):
    residuals = actual - forecast
    sns.histplot(residuals, kde=True, bins=30)
    plt.title("Forecast Residuals Distribution")
    plt.xlabel("Error (USD)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()


def plot_rolling_metrics(actual: np.ndarray, forecast: np.ndarray, window: int = 100):
    err = pd.Series(actual - forecast)
    rolling_rmse = err.rolling(window).apply(lambda e: np.sqrt(np.mean(e ** 2)))
    rolling_mape = (np.abs(err) / actual).rolling(window).mean() * 100

    plt.figure(figsize=(10, 5))
    plt.plot(rolling_rmse, label="Rolling RMSE")
    plt.plot(rolling_mape, label="Rolling MAPE (%)")
    plt.title(f"Rolling Error Metrics (window = {window})")
    plt.legend()
    plt.tight_layout()
    plt.show()


# -----------------------------------------------------------------
# 6. MAIN SCRIPT
# -----------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_PATH = "./output/bitcoin"
    DAYS_HISTORY = 30  # look‑back window for training
    FUTURE_STEPS = 10  # forecast horizon (hours)

    # ------------------ 6·1  ETL ------------------
    spark_df = etl_pipeline(DAYS_HISTORY, OUTPUT_PATH)

    # ------------------ 6·2  TRAIN ----------------
    model, scaler = train_rnn_model(spark_df, time_steps=20, hidden_size=64, epochs=5)

    # ------------------ 6·3  FORECAST ------------
    recent_prices = (
        spark_df.select("price").rdd.map(lambda r: r[0]).collect()[-20:]
    )
    future_preds = predict_future(model, scaler, recent_prices, future_steps=FUTURE_STEPS)

    # ------------------ 6·4  VISUALS -------------
    pdf = spark_df.toPandas()
    future_times = pd.date_range(start=pdf["time"].iloc[-1] + timedelta(hours=1), periods=FUTURE_STEPS, freq="H")

    plot_forecast(pdf["time"], pdf["price"], future_times, future_preds)

    # Because we don't have ground truth for the future yet, compute diagnostics on last 'FUTURE_STEPS' window
    actual_window = pdf["price"].iloc[-FUTURE_STEPS:].values
    rmse, mape = compute_metrics(actual_window, future_preds)
    print(f"\n⚙️  Diagnostics on last {FUTURE_STEPS} obs →  RMSE = {rmse:,.0f}  |  MAPE = {mape:,.2f}%")

    plot_residuals(actual_window, np.asarray(future_preds))
    plot_rolling_metrics(actual_window, np.asarray(future_preds), window=FUTURE_STEPS)
