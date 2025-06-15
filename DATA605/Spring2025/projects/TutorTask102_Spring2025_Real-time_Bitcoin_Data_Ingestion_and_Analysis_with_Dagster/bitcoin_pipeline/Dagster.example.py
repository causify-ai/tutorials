#!/usr/bin/env python
# coding: utf-8

# # Dagster Pipeline Example: Bitcoin Data Ingestion + Forecasting
#
# This notebook demonstrates how to use a Dagster-style pipeline to fetch, transform, store, and analyze real-time Bitcoin price data using the CoinGecko API.
#
# All logic is imported from `Dagster_utils.py`.

# ## Setup and Imports

from Dagster_utils import (
    fetch_bitcoin_price,
    process_price_data,
    save_to_csv,
    get_historical_bitcoin_data,
    calculate_moving_average,
    detect_trend,
    detect_anomalies_zscore,
    plot_price_with_moving_average,
    fit_arima_model,
    plot_arima_forecast
)

import pandas as pd
import matplotlib.pyplot as plt

# ## 1. Fetch Real-time Bitcoin Price

price_data = fetch_bitcoin_price()
df_live = process_price_data(price_data)

print(" Current Bitcoin Price:")
print(df_live)

# ## 2. Save Real-time Price to CSV

save_to_csv(df_live, filepath="bitcoin_prices.csv")
print("Data saved to bitcoin_prices.csv")

# ## 3. Load Historical Bitcoin Price Data

# Use 365 days for richer ARIMA forecasting
df_hist = get_historical_bitcoin_data(days=365)

# ## 4. Calculate Moving Average

df_ma = calculate_moving_average(df_hist, window_days=5)

# ## 5. Detect Trend and Anomalies

trend = detect_trend(df_ma)
print(f"Detected trend: {trend}")

df_anom = detect_anomalies_zscore(df_ma)
print("Detected anomalies:")
print(df_anom[df_anom["anomaly"] == True].head())

# ## 6. Plot Price with Moving Average

plot_price_with_moving_average(df_ma)

# ## 7. Forecast Future Prices with ARIMA

print("Forecasting Bitcoin prices for the next 30 days using ARIMA...")
forecast_df = fit_arima_model(df_hist, order=(5, 1, 0), forecast_steps=30)
plot_arima_forecast(forecast_df, forecast_steps=30)
