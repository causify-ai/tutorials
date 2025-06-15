import pandas as pd
import numpy as np
from prophet import Prophet
from utils.fetch_xray_trace_data import fetch_today_trace_data

def load_trace_data():
    return fetch_today_trace_data()

def compute_hourly_metrics(df):
    hourly = df.groupby("hour_str").agg({
        "processing_time_ms": ["mean", "max", "min", "std"],
        "error": lambda x: np.mean(x.astype(bool)),
        "data_volume_bytes": "sum",
        "trace_id": "count"
    }).reset_index()

    hourly.columns = [
        "hour_str", "latency_avg", "latency_max", "latency_min", "latency_std",
        "error_rate", "total_data_volume_bytes", "request_count"
    ]

    hourly["rolling_latency_avg"] = hourly["latency_avg"].rolling(window=3, min_periods=1).mean()
    hourly["rolling_error_rate"] = hourly["error_rate"].rolling(window=3, min_periods=1).mean()

    return hourly


def compute_daily_metrics(df):
    df_daily = df.copy()
    df_daily["date"] = df_daily["hour_str"].dt.date

    daily = df_daily.groupby("date").agg({
        "processing_time_ms": ["mean", "max", "min", "std"],
        "error": lambda x: np.mean(x.astype(bool)),
        "data_volume_bytes": "sum",
        "trace_id": "count"
    }).reset_index()

    daily.columns = [
        "date", "latency_avg", "latency_max", "latency_min", "latency_std",
        "error_rate", "total_data_volume_bytes", "request_count"
    ]

    daily["rolling_latency_avg"] = daily["latency_avg"].rolling(window=3, min_periods=1).mean()
    daily["rolling_error_rate"] = daily["error_rate"].rolling(window=3, min_periods=1).mean()

    return daily


def forecast_hourly_latency(hourly_df):
    prophet_df = hourly_df[["hour_str", "latency_avg"]].rename(columns={"hour_str": "ds", "latency_avg": "y"})
    model = Prophet(interval_width=0.95, daily_seasonality=False, weekly_seasonality=True)
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=24, freq='h')
    forecast = model.predict(future)

    merged = pd.merge(
        forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]],
        prophet_df, on="ds", how="left"
    )
    return merged


def forecast_daily_latency(daily_df):
    prophet_df = daily_df[["date", "latency_avg"]].rename(columns={"date": "ds", "latency_avg": "y"})
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
    model = Prophet(interval_width=0.95, daily_seasonality=True)
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=7, freq='D')
    forecast = model.predict(future)

    merged = pd.merge(
        forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]],
        prophet_df, on="ds", how="left"
    )
    return merged
