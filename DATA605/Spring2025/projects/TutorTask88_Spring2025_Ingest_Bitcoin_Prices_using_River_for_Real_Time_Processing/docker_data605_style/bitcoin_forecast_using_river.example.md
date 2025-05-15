# Bitcoin Forecasting with River — Example Notebook

A demonstration of using **River**, a Python library for online machine learning, to simulate a real-time learning environment for **Bitcoin price forecasting** using historical OHLC data from the **CoinGecko API**.

---

## Table of Contents

- [Project description](#project-description)
  - [Table of Contents](#table-of-contents)
- [Notebook Objective](#notebook-objective)
- [Functions and Logic](#functions-and-logic)
  - [1. Load OHLC Data](#1-load-ohlc-data)
  - [2. Feature Extraction](#2-feature-extraction)
  - [3. Rolling Window Setup](#3-rolling-window-setup)
  - [4. Model Training Loop](#4-model-training-loop)
  - [5. Logging and Output](#5-logging-and-output)
- [Key Insights and Takeaways](#key-insights-and-takeaways)
- [Dependencies](#dependencies)
- [References](#references)

---

## Project description

This project demonstrates how to simulate streaming time-series data for **Bitcoin** and perform **real-time forecasting** using **River**. The script evaluates three different online models using a rolling window of OHLC close prices and prints side-by-side comparisons between actual and predicted prices.

---

## How to run this notebook 
Run all cells top to bottom after ensuring template_utils.py is in same directory.

---

## Notebook Objective

- Simulate a real-time stream of **closing Bitcoin prices**.
- Build lag-based features using a **rolling window**.
- Predict the next price using three different **online learners**.
- Evaluate model performance using **Mean Absolute Error (MAE)**.
- Display model weights and rolling volatility.

---

## Functions and Logic

### 1. Load OHLC Data
- `get_coin_ohlc(days=1)` from `bitcoin_forecast_utils.py` is used.
- Retrieves last day’s worth of OHLC candles.

### 2. Feature Extraction
- `build_rolling_features()` builds lag features.
- Uses only recent 5 closing prices from deque.

### 3. Rolling Window Setup
```python
rolling_prices = deque(maxlen=5)
```
- Maintains a sliding window for recent close prices.

### 4. Model Training Loop
For each of the ~30 price points:
- Extracts features.
- Predicts price with each model.
- Updates the model with true value.
- Logs prediction and error.

### 5. Logging and Output
- MAE is tracked and printed per step.
- Model weights are printed at the end.
- Outputs are printed to console only (no plots or UI).

---

## Key Insights and Takeaways

- Demonstrates how online learners in River evolve incrementally.
- Shows how prediction performance (MAE) varies with model choice.
- Highlights how pipelines (scaling + regression) improve learning stability.

---

## Dependencies

- `river`
- `pandas`
- `matplotlib`
- `collections`
- `bitcoin_forecast_utils.py`
-`requirements.txt`

---

## References

- [River ML Docs](https://riverml.xyz/latest/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [`bitcoin_forecast_utils.py`](../bitcoin_forecast_utils.py)
