import pandas as pd
from prophet import Prophet
from config import PROPHET_FUTURE_PERIODS, PROPHET_FREQ

def run_prophet(df):
    if df.empty or 'price' not in df.columns:
        raise ValueError("Missing 'price' column or empty DataFrame.")

    df_prophet = df.reset_index().rename(columns={'timestamp': 'ds', 'price': 'y'})
    df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)

    df_prophet = df_prophet.dropna(subset=['ds', 'y'])

    if len(df_prophet) < 10:
        raise ValueError("Insufficient data points for Prophet.")

    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=PROPHET_FUTURE_PERIODS, freq=PROPHET_FREQ)
    forecast = model.predict(future)

    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast = forecast.dropna(subset=['yhat'])  # guard against NaNs

    return forecast
