<!-- toc -->

* [OpenRefine Bitcoin API Tutorial](#openrefine-bitcoin-api-tutorial)

  * [Overview](#overview)
  * [General Guidelines](#general-guidelines)
  * [API Structure](#api-structure)

    * [1. Data Ingestion](#1-data-ingestion)
    * [2. Data Preparation and Cleaning](#2-data-preparation-and-cleaning)
    * [3. Feature Engineering](#3-feature-engineering)
    * [4. Forecast Modeling](#4-forecast-modeling)
    * [5. Visualizations](#5-visualizations)
  * [References and Citations](#references-and-citations)
  * [Future Enhancements](#future-enhancements)

<!-- tocstop -->

# OpenRefine Bitcoin API Tutorial

This API layer supports the project "Real-time Bitcoin Price Analysis using OpenRefine" and is implemented in `openrefine_utils.py`. It defines reusable Python functions for fetching, validating, enriching, forecasting, and visualizing Bitcoin price data cleaned using OpenRefine. All functions are designed to work seamlessly with 15-minute interval data and support integration into Jupyter notebooks or pipeline environments.

## Overview

This notebook organizes the utility functions under each major step of the Bitcoin forecasting project. It demonstrates how data flows through ingestion, preprocessing, model training, and visualization, providing a clear understanding of the workflow.

## General Guidelines

* All utility functions are implemented in `openrefine_utils.py`.
* These functions are reused across both the API and example notebooks.
* All functions follow modular design and are documented with consistent docstrings.
* Forecasting is done using the `Prophet` library with 15-minute data cleaned and extracted using OpenRefine.

## API Structure

### 1. Data Ingestion

**Function:** `fetch_bitcoin_data_kucoin()`

* Fetches 15-minute OHLCV Bitcoin price data from the KuCoin API.
* Returns a DataFrame with open, high, low, close, volume, and timestamp columns.

**Function:** `save_to_csv(df, filename)`

* Saves any DataFrame to a CSV file.
* Used to export raw or cleaned data before and after OpenRefine processing.

### 2. Data Preparation and Cleaning

**Function:** `load_cleaned_data(filepath)`

* Loads the cleaned CSV file exported from OpenRefine.
* Ensures timestamps are parsed and the schema is analysis-ready.

**Function:** `validate_cleaned_data(df)`

* Validates the structure and consistency of cleaned data.
* Ensures no missing values, logical price ranges, and monotonic timestamps.

**Function:** `resample_data(df, interval='1H')`

* Resamples data to hourly or daily intervals for exploratory visualization.
* Note: Resampled data is not used in modeling, only for interpretation.

### 3. Feature Engineering

**Function:** `calculate_technical_indicators(df)`

* Adds moving averages (7, 24), Bollinger Bands, and momentum indicators.
* Enhances the dataset for trend and volatility analysis.

**Function:** `prepare_forecast_data(df)`

* Prepares time series data for Prophet by renaming columns and formatting.
* Returns a DataFrame with Prophet-compatible `ds` and `y` columns.

### 4. Forecast Modeling

**Function:** `train_model(train_df, periods=96)`

* Trains a Prophet model on the prepared dataset.
* Forecasts future values for the specified horizon (e.g., 24 hours).

### 5. Visualizations

**Function:** `plot_forecast(train_df, forecast_df)`

* Plots actual vs forecasted values with confidence bands using Plotly.

**Function:** `plot_comparision(test_df, forecast_df)`

* Merges actual vs predicted values and visualizes overlap and deviation for detailed comparision.

**Function:** `plot_technical_indicators(df)`

* An interactive plot showing price trend, moving averages, and Bollinger Bands.


## References and Citations

* OpenRefine: [https://openrefine.org/](https://openrefine.org/)
* KuCoin API Docs: [https://www.kucoin.com/docs/rest/spot-trading/market/get-klines](https://www.kucoin.com/docs/rest/spot-trading/market/get-klines)
* KuCoin BTC-USDT Market: [https://www.kucoin.com/en-us/trade/BTC-USDT](https://www.kucoin.com/en-us/trade/BTC-USDT)
* Prophet Docs: [https://facebook.github.io/prophet/docs/quick\_start.html](https://facebook.github.io/prophet/docs/quick_start.html)
* Plotly: [https://plotly.com/python/](https://plotly.com/python/)

## Future Enhancements

* Add hyperparameter tuning support for Prophet configuration.
* Integrate OpenRefine steps directly using its API.
* Support real-time updates and dynamic retraining.
* Modularize forecast intervals (30 min, 1 hour, 6 hours, etc.).
* Add logging and exception handling for each function.
