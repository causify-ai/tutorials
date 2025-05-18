<!-- toc -->

- [LightGBM Bitcoin API Tutorial](#lightgbm-bitcoin-api-tutorial)
  * [General Guidelines](#general-guidelines)
  * [API Overview](#api-overview)
    + [1. Fetch Real-time Price](#1-fetch-real-time-price)
    + [2. Format Live Price Data](#2-format-live-price-data)
    + [3. Retrieve Historical Data](#3-retrieve-historical-data)
    + [4. Feature Engineering](#4-feature-engineering)
    + [5. Compute Moving Averages](#5-compute-moving-averages)
    + [6. Detect Trend](#6-detect-trend)
    + [7. Detect Anomalies](#7-detect-anomalies)
    + [8. Visualize Price and MA](#8-visualize-price-and-ma)
  * [References and Citations](#references-and-citations)
  * [Future Improvements](#future-improvements)
  * [Additional Features to Explore](#additional-features-to-explore)

<!-- tocstop -->

---

# LightGBM Bitcoin API Tutorial

This API layer supports the project **"Real-time Bitcoin Price Forecasting using LightGBM"** and is implemented in `LightGBM_utils.py`. It defines modular functions for fetching, analyzing, and visualizing Bitcoin price data, with a focus on machine learning readiness and time-series trends.

---

## General Guidelines

- All core functions are implemented in `LightGBM_utils.py`
- This API file does **not perform training or forecasting**
- Designed for use inside ingestion pipelines, notebooks, and forecasting apps
- Works with both **live** and **historical** price data

---

## API Overview

---

### 1. Fetch Real-time Price

**Function:** `fetch_bitcoin_price()`

- Calls CoinGecko's `/simple/price` endpoint  
- Returns: dictionary with `timestamp` and `price`

---

### 2. Format Live Price Data

**Function:** `process_price_data(data)`

- Converts a raw dictionary to a single-row DataFrame  
- Used for appending new points or merging with historical data

---

### 3. Retrieve Historical Data

**Function:** `get_historical_bitcoin_data(days=365)`

- Queries CoinGecko’s `/market_chart` endpoint  
- Auto-switches between `daily` and `hourly` based on days  
- Returns: DataFrame with `timestamp` and `price`

---

### 4. Feature Engineering

**Function:** `create_features(df)`

- Adds lag-based and time-based features:
  - `minute`, `hour`, `dayofweek`  
  - `lag_1`, `lag_2`, `rolling_mean_3`, `rolling_std_3`  
- Used before training ML models like LightGBM

---

### 5. Compute Moving Averages

**Function:** `calculate_moving_average(df, window_days=7)`

- Adds a `moving_average` column  
- Computes rolling average of price using the specified window  
- Useful for trend smoothing and signal extraction

---

### 6. Detect Trend

**Function:** `detect_trend(df)`

- Applies linear regression to time-series index vs. price  
- Classifies trend as:
  - `"upward"`  
  - `"downward"`  
  - `"flat"`

---

### 7. Detect Anomalies

**Function:** `detect_anomalies_zscore(df, threshold=2.5)`

- Adds `z_score` and `anomaly` boolean columns  
- Flags anomalies where price deviates beyond the given threshold  
- Based on standard Z-score statistical outlier detection

---

### 8. Visualize Price and MA

**Function:** `plot_price_with_moving_average(df)`

- Plots Bitcoin price over time with overlayed moving average  
- Can be extended to include anomalies, forecasts, or confidence bands  
- Requires `timestamp`, `price`, and `moving_average` columns

---
## References and Citations

- [LightGBM Docs](https://lightgbm.readthedocs.io/)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
- [scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [StatsModels Z-score](https://www.statsmodels.org/)

---

## Future Improvements

- **Integrate hyperparameter tuning with Optuna or GridSearchCV**  
  Improve model accuracy and generalization by tuning LightGBM parameters such as `num_leaves`, `learning_rate`, and `max_depth`.

- **Add prediction intervals using quantile regression**  
  Use LightGBM’s `"quantile"` objective to generate upper and lower bounds, enabling uncertainty-aware forecasting.

- **Support real-time streaming via Binance WebSocket**  
  Replace periodic CoinGecko pulls with high-frequency live data from Binance for second-level updates.

- **Deploy anomaly detection alerts in forecast pipeline**  
  Trigger alerts when the predicted price deviates significantly from actual values, based on dynamic Z-score thresholds.
---

## Additional Features to Explore
**In CoinGecko API:**

- Market cap, total volume, and circulating supply  
- Sentiment data (`sentiment_votes_up_percentage`)  
- Price data for other coins (Ethereum, Solana, etc.)  
- Exchange-level BTC pricing via `/tickers`  
- Global stats (BTC dominance, volume change, active markets)  
- Coin categories and ecosystem tags  
- Historical OHLC (Open-High-Low-Close) candle data  
- Developer and community activity (GitHub, Reddit)

---

**In LightGBM:**

- Hyperparameter tuning via GridSearchCV or Optuna  
- GPU-accelerated training (`device_type='gpu'`)  
- Early stopping and validation-based pruning  
- Native handling of categorical features  
- Quantile regression for prediction intervals  
- Feature importance visualization  
- Explainability using SHAP values  
- Cross-validation using `lightgbm.cv()'