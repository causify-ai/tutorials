<!-- toc -->

- [Dagster Bitcoin API Tutorial](#dagster-bitcoin-api-tutorial)
  * [General Guidelines](#general-guidelines)
  * [API Overview](#api-overview)
    + [1. Fetch Real-time Price](#1-fetch-real-time-price)
    + [2. Format Price Data](#2-format-price-data)
    + [3. Retrieve Historical Data](#3-retrieve-historical-data)
    + [4. Compute Moving Averages](#4-compute-moving-averages)
    + [5. Detect Trend](#5-detect-trend)
    + [6. Detect Anomalies](#6-detect-anomalies)
    + [7. Visualize Price and MA](#7-visualize-price-and-ma)
  * [References and Citations](#references-and-citations)
  * [Future Improvements](#future-improvements)
  * [Additional Features to Explore](#additional-features-to-explore)

<!-- tocstop -->

---

# Dagster Bitcoin API Tutorial

This API layer supports the project "Real-time Bitcoin Data Ingestion and Analysis with Dagster" and is implemented in `template_utils.py`. It defines all the logic for fetching, processing, analyzing, and visualizing Bitcoin price data using CoinGecko API and is fully reusable within Dagster solids or Jupyter notebooks.

---

## Table of Contents

This markdown documents:

- Real-time price fetch  
- Historical data analysis  
- Trend detection and anomaly detection  
- Plotting and insights 


---

## General Guidelines

- Code is implemented in `template_utils.py`.
- This file is reused in both API and example notebooks.
- Modular and clear functions make integration with Dagster solids easier.
- Enables scheduled ingestion and reproducible analytics.

---

## API Overview

### 1. Fetch Real-time Price

**Function:** `fetch_bitcoin_price()`

- Uses CoinGecko's `/simple/price` endpoint.  
- Returns a dictionary with the current BTC/USD price and timestamp.  
- Used in real-time tracking and ingestion.

---

### 2. Format Price Data

**Function:** `process_price_data(data)`

- Takes the raw dictionary and converts it into a Pandas DataFrame.  
- One-row structure for easy CSV export or merge.

---

### 3. Retrieve Historical Data

**Function:** `get_historical_bitcoin_data(days=30)`

- Fetches market price data using CoinGecko's `/market_chart` endpoint.  
- Returns date-wise price DataFrame for time series analysis.  
- Default period: 30 days, but customizable.

---

### 4. Compute Moving Averages

**Function:** `calculate_moving_average(df, window_days=7)`

- Adds a `moving_average` column to the input DataFrame.  
- Rolling average is based on the number of days specified.  
- Assumes high-frequency price data (e.g., 5-min intervals).

---

### 5. Detect Trend

**Function:** `detect_trend(df)`

- Performs linear regression over time index vs price.  
- Classifies trend as "upward", "downward", or "flat".  
- Basic but effective indicator of market momentum.

---

### 6. Detect Anomalies

**Function:** `detect_anomalies_zscore(df, threshold=2.5)`

- Adds `z_score` and `anomaly` flag to DataFrame.  
- Flags outliers in price using statistical thresholding.  
- Helps spot unusual market behavior.

---

### 7. Visualize Price and MA

**Function:** `plot_price_with_moving_average(df)`

- Uses matplotlib to overlay price and moving average.  
- Clean visualization of trends and anomalies.  
- Can be extended for additional chart types.

---

## References and Citations

- Dagster Docs: https://docs.dagster.io  
- CoinGecko API Docs: https://www.coingecko.com/en/api/documentation  
- Pandas Library: https://pandas.pydata.org  
- Matplotlib: https://matplotlib.org/  
- Scipy Linear Regression: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html

---

## Future Improvements

- Use SQL/TimescaleDB instead of flat CSV for long-term data storage.  
- Add retry logic and error logging in API fetch functions.  
- Modularize configuration (e.g., API URL, file path, window sizes) via config files or Dagster resources.  
- Integrate unit tests for utility functions.  
- Add logging/alerts using Dagster's built-in alert hooks.

---

## Additional Features to Explore

**In CoinGecko API:**

- Market cap, volume, and sentiment data  
- Price data for other coins (e.g., Ethereum, Solana)  
- Exchange-level price data  
- Global metrics and coin categories  

**In Dagster:**

- Dagster sensors for event-driven triggers  
- Partitioning for backfilling missing data  
- Asset materialization for versioned datasets  
- Scheduled jobs with custom intervals  
- Dagster cloud deployment

---
