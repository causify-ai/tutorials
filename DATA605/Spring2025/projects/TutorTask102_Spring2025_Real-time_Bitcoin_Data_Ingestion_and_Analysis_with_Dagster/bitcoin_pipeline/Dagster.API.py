#!/usr/bin/env python
# coding: utf-8

# # Dagster Bitcoin API
#
# This script demonstrates core utility functions from `Dagster_utils.py` for interacting with the CoinGecko API, storing live prices, and performing time-series analysis on Bitcoin price data.
#
# It serves as a clean, minimal demo of your pipeline logic, separated from the full example implementation.

# ## References
# - CoinGecko API Docs: https://www.coingecko.com/en/api
# - Dagster Docs: https://docs.dagster.io

# ## Imports

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

# ## 1. Fetch Current Price from CoinGecko

live_price = fetch_bitcoin_price()
print("Live Bitcoin Price (USD):")
print(live_price)

# ## 2. Format Live Price into DataFrame

df_price = process_price_data(live_price)
print("\n Structured Live Price Data:")
print(df_price)

# ## 3. Save Real-time Data to CSV

save_to_csv(df_price, filepath="bitcoin_prices.csv")
print("\n Saved to 'bitcoin_prices.csv'")

# ## 4. Fetch Historical Bitcoin Price Data

df_hist = get_historical_bitcoin_data(days=365)
print("\n Sample Historical Data (365 days):")
print(df_hist.head())

# ## 5. Calculate 5-Day Moving Average

df_ma = calculate_moving_average(df_hist, window_days=5)
print("\n With 5-Day Moving Average:")
print(df_ma.head())

# ## 6. Detect Basic Trend

trend = detect_trend(df_ma)
print(f"\n Detected Trend Direction: {trend}")

# ## 7. Identify Anomalies (Z-Score Based)

df_anom = detect_anomalies_zscore(df_ma)
print("\n Anomalies Detected:")
print(df_anom[df_anom["anomaly"] == True].head())

# ## 8. Visualize Price with Moving Average

print("\n Plotting price with moving average:")
plot_price_with_moving_average(df_anom)

# ## 9. ARIMA Forecasting

print("\n Forecasting next 30 days with ARIMA(5,1,0):")
forecast_df = fit_arima_model(df_hist, order=(5, 1, 0), forecast_steps=30)
plot_arima_forecast(forecast_df, forecast_steps=30)
