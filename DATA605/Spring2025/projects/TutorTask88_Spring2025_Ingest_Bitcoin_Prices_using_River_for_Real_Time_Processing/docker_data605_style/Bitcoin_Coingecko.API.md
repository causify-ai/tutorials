# Bitcoin_Coingeko.API — API Notebook Documentation

This notebook serves as a **streaming simulation environment** to test and validate Bitcoin price ingestion, feature construction, and real-time forecasting using River models.

---

## Table of Contents

* [Purpose of this Notebook](#purpose-of-this-notebook)
* [Functions and Features Demonstrated](#key-functions--code-blocks-used)

  * [1. Retrieve OHLC Data](#1-get_coin_ohlcdays1)
  * [2. Rolling Window Setup](#2-rolling-window-setup)
  * [3. Model Initialization](#3-model-initialization)
  * [4. Streaming Loop Simulation](#4-streaming-loop-simulation)
  * [5. Evaluation and Logging](#5-evaluation-and-logging)
  * [6. Output](#6-output-console-only)
* [Insights and Limitations](#insights-this-notebook-provides)
* [Dependencies](#dependencies)
* [References](#references)
---

## Purpose of this Notebook

* Simulate **real-time price forecasting** using live-like data.
* Incrementally train a River regression model using a rolling window of lagged Bitcoin prices.
* Test feature engineering and model behavior with respect to prediction accuracy and weight learning.
* Compare predictions from multiple online learners (Linear Regression, Tree, Pipeline).

---
## How to run this notebook 
Run all cells top to bottom after ensuring template_utils.py is in same directory.

---
##  Key Functions & Code Blocks Used

### 1. `get_coin_ohlc(days=1)`

* Fetches 1-day OHLC (Open, High, Low, Close) Bitcoin data.
* Used as a stand-in for real-time incoming price stream.
* Returns a `DataFrame` of recent closing prices.

### 2. Rolling Window Setup

```python
rolling_prices = deque(maxlen=5)
```

* Maintains a rolling window of the last 5 prices.
* Enables lag-based feature construction.

### 3. Model Initialization

Three models are initialized:

Each model is trained online using `.learn_one()`.

### 4. Streaming Loop Simulation

* Iterates over \~30 close price values from OHLC data.
* Builds lag features (`price_lag_0` to `price_lag_4`) using `build_rolling_features()`.
* Performs:

  * Prediction with each model
  * Model update (learning)
  * Logging of MAE and predictions

### 5. Evaluation and Logging

Predictions and actuals are logged into:

```python
actual_log, lr_log, tree_log, pipe_log, vol_log
```

Weights are printed from the `pipeline_model`:

```python
pipeline_model[-1].weights
```

### 6. Output (Console Only)

* A side-by-side table of:

  * Actual price
  * Predicted price from each model
  * Rolling volatility
* Printed model weights at the end
---
### Native API-Based Streaming 

This section showcases real-time Bitcoin price forecasting using River's **native APIs** (`StandardScaler`, `LinearRegression`, and `MAE`) without pipeline wrappers.  
It uses a rolling window of lagged prices to create features and updates the model incrementally via `learn_one()` after each price observation.  
Predictions are made using `predict_one()`, and performance is tracked using `MAE` in real-time.  
This approach provides a transparent and modular example of **streaming online learning** with River.

---

## Insights This Notebook Provides

* Validates feature engineering (`price_lag_*`)
* Shows how MAE improves (or not) over time
* Compares online learners on real BTC data
* Verifies stability of model weights

---


## Dependencies

* `river`
* `pandas`
* `collections.deque`
* `template_utils.py` must be in the same directory
* `requirements.txt`

## References

- [River: Online machine learning for Python](https://riverml.xyz/latest/)
- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [River LinearRegression API](https://riverml.xyz/latest/api/linear_model/LinearRegression/)
- [River StandardScaler API](https://riverml.xyz/latest/api/preprocessing/StandardScaler/)
- [River Metrics (MAE, Accuracy, etc.)](https://riverml.xyz/latest/api/metrics/)
- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [Python `collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
- [Real-Time Machine Learning Concepts – AWS Blog](https://aws.amazon.com/blogs/machine-learning/building-real-time-prediction-systems-with-online-learning/)

