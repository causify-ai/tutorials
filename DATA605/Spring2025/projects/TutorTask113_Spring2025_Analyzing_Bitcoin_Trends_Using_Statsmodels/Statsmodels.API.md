
# Statsmodels Tutorial

<!-- toc -->

- [Tutorial Template for Native API of the tool used](#tutorial-template-for-native-api-of-the-tool-used)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
  * [Overview](#overview)
  * [Function Descriptions](#function-descriptions)
    + [fetch_historical_data()](#fetch_historical_data)
    + [simulate_realtime()](#simulate_realtime)
    + [plot_time_series()](#plot_time_series)
    + [plot_acf_pacf()](#plot_acf_pacf)
    + [run_arima_analysis()](#run_arima_analysis)
    + [plot_forecast()](#plot_forecast)
    + [save_to_csv()](#save_to_csv)
    + [fetch_and_process_data()](#fetch_and_process_data)
  * [Integration Example](#integration-example)

<!-- tocstop -->

# Tutorial Template for Native API of the tool used

This document outlines the native API wrapper built using the `statsmodels` library and CoinGecko API. It is implemented in `statsmodels_utils.py` and supports real-time forecasting of Bitcoin prices.

## Table of Contents

This markdown file includes a table of contents and hierarchical structure to improve navigation and readability.

### Hierarchy

```
# Level 1 (Used as title)
## Level 2
### Level 3
```

## General Guidelines

- Follow the structure and practices in [README](/DATA605/DATA605_Spring2025/README.md).
- This tutorial explains how the API functions work and how they are applied in `statsmodels.API.ipynb`.
- This file is named as `statsmodels.API.md` following naming conventions.

---

## Overview

The native API layer provides Python functions to ingest, process, and analyze Bitcoin price data. It uses CoinGecko as the data source and statsmodels for statistical modeling. Each function is modular and reusable.

## Function Descriptions

### fetch_historical_data()
Fetches 1-day BTC/USD price data at 1-minute intervals using the CoinGecko `/market_chart` endpoint. Returns a resampled and cleaned DataFrame.

### simulate_realtime(df, minutes=3)
Simulates streaming data by appending 1-minute interval price points to the existing DataFrame for a specified number of minutes using the CoinGecko `/simple/price` endpoint.

### plot_time_series(df)
Plots the current Bitcoin time series using matplotlib. Useful for visualizing recent price trends.

### plot_acf_pacf(df, lags=40)
Generates ACF and PACF plots to diagnose the lag structure and help choose ARIMA(p, d, q) parameters.

### run_arima_analysis(df)
Fits an ARIMA(2,1,2) model on the BTC price series and forecasts the next 30 data points. Returns the fitted model and forecast values.

### plot_forecast(df, forecast)
Visualizes actual BTC prices alongside the 30-minute ARIMA forecast. Highlights predictive performance.

### save_to_csv(df, forecast)
Writes the current BTC data and its forecast to two CSV files: `btc_full_data.csv` and `btc_price_forecast.csv`.

### fetch_and_process_data(days, filename, title)
General-purpose function to fetch and resample Bitcoin data for 1, 30, or 365 days. Saves and plots the result.

---

## Integration Example

These functions are used in sequence in the `statsmodels.API.ipynb` notebook. Example usage:

```python
import statsmodels_utils as smu
btc_df = smu.fetch_historical_data()
btc_df = smu.simulate_realtime(btc_df, minutes=3)
smu.plot_time_series(btc_df)
smu.plot_acf_pacf(btc_df)
model, forecast = smu.run_arima_analysis(btc_df)
smu.plot_forecast(btc_df, forecast)
smu.save_to_csv(btc_df, forecast)
```

Each step in the notebook corresponds directly to an API function described here.

---

This concludes the tutorial for the native API built on `statsmodels` for real-time Bitcoin price analysis.
