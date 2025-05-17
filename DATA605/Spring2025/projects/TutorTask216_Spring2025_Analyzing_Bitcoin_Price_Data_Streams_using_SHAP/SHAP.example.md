# SHAP Bitcoin Forecasting Example

This project demonstrates how to build a real-time Bitcoin price prediction pipeline using **XGBoost**, with interpretability powered by **SHAP (SHapley Additive Explanations)**.

The pipeline uses **hourly Bitcoin price data**, retrieved live using the CoinGecko API, and applies engineered time series features (lags, volatility) to forecast next-hour price movements.

## Table of Contents

This markdown provides a full breakdown of data loading, analysis, modeling, and interpretation using SHAP. All major processes are modularized for reusability.

<!-- toc -->

- [SHAP Bitcoin Forecasting Example](#shap-bitcoin-forecasting-example)
  - [Table of Contents](#table-of-contents)
    - [Hierarchy](#hierarchy)
  - [General Guidelines](#general-guidelines)
- [1. Overview](#1-overview)
- [2. Data Ingestion and Wrappers](#2-data-ingestion-and-wrappers)
- [3. Data Exploration](#3-data-exploration)
- [4. Stationarity Testing](#4-stationarity-testing)
- [5. Modeling Pipeline](#5-modeling-pipeline)
- [6. SHAP-Based Interpretability](#6-shap-based-interpretability)
  - [6.1 Global Explanations](#61-global-explanations)
  - [6.2 Local Explanations](#62-local-explanations)
- [7. Modularity and Utilities](#7-modularity-and-utilities)
- [8. Future Extensions](#8-future-extensions)
- [9. File Naming Convention](#9-file-naming-convention)

<!-- tocstop -->

### Hierarchy

```
# Level 1 (Used as title)
## Level 2
### Level 3
```

## General Guidelines

- This documentation complements the notebook: `SHAP.example.ipynb`
- The SHAP Python API is used for model interpretability.
- All critical logic is modularized in `SHAP_utils.py`

---

## 1. Overview

This notebook predicts the **next-hour price** of Bitcoin using recent price/volume/market cap trends. It integrates:

- Real-time data fetching via the **CoinGecko API**
- Time series feature engineering (lags + rolling stats)
- Model training and SHAP interpretability

---

## 2. Data Ingestion and Wrappers

We use a custom wrapper around the **CoinGecko API** to pull hourly market data in real time.

### Wrapper: `fetch_market_chart_data()` + `load_realtime_btc_data()`

- Retrieves price, market cap, and volume for Bitcoin
- Combines them into a unified `pandas.DataFrame`
- Configurable via a YAML or dictionary-based API setup

Example function call:

```python
df = load_realtime_btc_data(days=30, currency="usd")
```

### Utility: `save_market_data()`

Saves raw ingested data with a timestamped filename for reproducibility.

---

## 3. Data Exploration

We built a comprehensive **EDA wrapper suite** to streamline visualization:

- **Trend plots**: `plot_price_over_time()`, `plot_volume_over_time()`, `plot_market_cap_over_time()`
- **Rolling averages**: `plot_rolling_mean()`, `plot_multiple_rolling_means()`
- **Distribution analysis**: `plot_distribution()`, `plot_boxplot_by_hour()`
- **Scatterplots**: `plot_scatter_price_vs_volume()`, `plot_scatter_price_vs_marketcap()`
- **Correlation heatmap**: `plot_correlation_heatmap()`
- **Seasonality**: `plot_hourly_average()`

These functions are available inside `src/preprocessing/eda_hourly_data.py`.

---

## 4. Stationarity Testing

We test for time series stationarity using:

### `plot_rolling_stats()`

Visualizes rolling mean and std deviation to assess trends and variance drift.

### `run_adf_test()`

Runs the **Augmented Dickey-Fuller test**, printing test statistic, p-value, and critical values for decision-making.

This helps determine whether differencing or detrending is required.

These functions are available inside `src/preprocessing/stationarity_checks.py`.

---

## 5. Modeling Pipeline

The forecasting model uses:

- **XGBRegressor** (from `xgboost`)
- Train-test split (80-20)
- Evaluation metrics:
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)
  - R² Score

The model predicts `price_t+1` based on engineered features like `price_lag_1`, `price_ma_24`, and `volume_std_6`.

---

## 6. SHAP-Based Interpretability

After training, we interpret the XGBoost model using **SHAP**.

### 6.1 Global Explanations

Wrapped inside `SHAPAnalyzer`:

- `.plot_global_importance()` → Bar plot of mean absolute SHAP values
- `.plot_summary_beeswarm()` → Beeswarm plot for feature-wise SHAP value distribution

These help identify which features consistently influence model predictions.

### 6.2 Local Explanations

Also provided by `SHAPAnalyzer`:

- `.plot_local_waterfall()` → Waterfall plot explaining one prediction
- `.plot_dependence()` → Interaction-aware scatterplot for one feature
- `.plot_decision()` → Cumulative contribution plot across features

All plots are interactive or publication-ready and enable granular transparency.

---

## 7. Modularity and Utilities

The project is fully modularized:

- **Data ingestion**: `src/ingestion/fetch_data.py`
- **EDA wrappers**: `src/preprocessing/eda_hourly_data.py`
- **Stationarity**: `src/preprocessing/stationarity_checks.py`
- **SHAP interpretation**: `src/shap_utils/shap_analysis.py`

This makes the pipeline easy to extend for other time frequencies (e.g., daily data) or other assets (e.g., Ethereum).

---

## 8. Future Extensions

- Re-run the pipeline on **daily-level Bitcoin data** for broader trend forecasting
- Use alternative regressors like **LightGBM** or **LSTM** for comparison
- Add **online training** to adapt the model over time
- Integrate alerts or signal generation from SHAP-localized anomalies

---

## 9. File Naming Convention

The naming structure follows DATA605 conventions:

```
SHAP.example.ipynb       ← The notebook
SHAP.example.md          ← This README
```

These files showcase how SHAP can be applied in practical, real-time scenarios using structured wrappers and interpretable machine learning.
