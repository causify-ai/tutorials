from dagster import op
from bitcoin_pipeline.Dagster_utils import (
    fetch_bitcoin_price,
    process_price_data,
    save_to_csv,
    get_historical_bitcoin_data,
    calculate_moving_average,
    detect_trend,
    detect_anomalies_zscore,
    fit_arima_model
)

@op
def fetch_price_op():
    return fetch_bitcoin_price()

@op
def process_price_op(data):
    return process_price_data(data)

@op
def save_csv_op(df):
    save_to_csv(df, filepath="bitcoin_prices.csv")

@op
def fetch_historical_op():
    return get_historical_bitcoin_data(days=365)

@op
def moving_average_op(df):
    return calculate_moving_average(df, window_days=5)

@op
def detect_trend_op(df):
    return detect_trend(df)

@op
def detect_anomalies_op(df):
    return detect_anomalies_zscore(df)

@op
def forecast_op(df):
    return fit_arima_model(df, order=(5, 1, 0), forecast_steps=30)
