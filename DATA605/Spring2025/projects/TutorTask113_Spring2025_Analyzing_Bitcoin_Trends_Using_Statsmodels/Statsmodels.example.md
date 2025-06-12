# saving the statsmodels.API.md content into a .md file directly from the known final content

api_md_content = """
# Statsmodels Bitcoin API Tutorial

This API layer supports the project "Bitcoin Price Forecasting with Statsmodels" and is implemented in `statsmodels_utils.py`. It defines reusable functions for fetching, processing, analyzing, and visualizing Bitcoin price data using the CoinGecko API. These functions can be integrated into notebooks, scripts, or modular pipelines.

---

## Table of Contents

- Project Context
- General Guidelines
- API Overview
  1. Fetch Historical Data
  2. Simulate Real-time Streaming
  3. Plot Time Series
  4. Plot ACF and PACF
  5. Fit ARIMA Model and Forecast
  6. Save Forecast to CSV
  7. Load and Compare Long-Range Data
- References and Citations
- Future Improvements
- Additional Features to Explore

---

## Project Context

This API underpins a time series forecasting system that simulates real-time Bitcoin price collection and uses ARIMA models from the `Statsmodels` library to predict short-term future prices. All components are modularized in the `Statsmodels_utils.py` utility layer.

---

## General Guidelines

- Code is implemented in `Statsmodels_utils.py`.
- This module is used in both `Statsmodels.API.ipynb` and `Statsmodels.example.ipynb`.
- All logic is structured into functions to support reuse, testing, and easy integration.
- Functions are intended to support both real-time simulation and historical backtesting.

---

## API Overview

### 1. Fetch Historical Data
Function: `fetch_historical_data()`

- Uses CoinGecko's `/market_chart` endpoint.
- Returns a 1-day DataFrame of 1-minute Bitcoin prices.
- Resampled and cleaned for uniform frequency.

---

### 2. Simulate Real-time Streaming
Function: `simulate_realtime(df, minutes=3)`

- Appends 1 new price point per minute using CoinGecko's `/simple/price` endpoint.
- Simulates real-time ingestion for short-term ARIMA forecasting.

---

### 3. Plot Time Series
Function: `plot_time_series(df)`

- Plots the time series for recent BTC prices.
- Used for visual inspection before model fitting or autocorrelation analysis.

---

### 4. Plot ACF and PACF
Function: `plot_acf_pacf(df, lags=40)`

- Uses statsmodels to compute and plot:
  - ACF (Autocorrelation Function)
  - PACF (Partial Autocorrelation Function)
- Aids in identifying ARIMA parameters (p, d, q).

---

### 5. Fit ARIMA Model and Forecast
Function: `run_arima_analysis(df)`

- Resamples and forwards-fills the BTC price series.
- Applies ARIMA(2,1,2) modeling.
- Forecasts next 30 minutes of price.

---

### 6. Save Forecast to CSV
Function: `save_to_csv(df, forecast)`

- Saves the current time series and forecast results to:
  - `btc_full_data.csv`
  - `btc_price_forecast.csv`

---

### 7. Load and Compare Long-Range Data
Function: `fetch_and_process_data(days, filename, title)`

- Fetches and resamples price data for 1, 30, or 365 days.
- Saves to CSV and plots price trends.
- Used for context and comparison with real-time data.

---

## References and Citations

- Statsmodels: https://www.statsmodels.org
- CoinGecko API: https://www.coingecko.com/en/api/documentation
- Pandas: https://pandas.pydata.org
- Matplotlib: https://matplotlib.org

---

## Future Improvements

- Automate ARIMA order selection using AIC or auto_arima.
- Add confidence intervals to forecasts.
- Modularize parameters like ARIMA(p,d,q) and forecast horizon.
- Extend simulation to multiple cryptocurrencies.
- Add more Time series methods

---

## Additional Features to Explore

- Use alternative time series models (Prophet, SARIMA).
- Integrate anomaly detection (e.g., z-score, change points).
- Add Docker deployment for periodic forecasting.
- Enable streaming pipeline with Apache Kafka or Dagster.

---

This API provides a robust and clear interface to support time series forecasting with real-time or historical Bitcoin data using `statsmodels`.
"""

# Save file
api_md_path = "/mnt/data/statsmodels.API.md"
with open(api_md_path, "w") as f:
    f.write(api_md_content)

api_md_path
