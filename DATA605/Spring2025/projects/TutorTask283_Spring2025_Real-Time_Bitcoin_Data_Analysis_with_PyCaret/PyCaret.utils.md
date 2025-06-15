

## Documentation: `PyCaret_utils.py`

This module contains reusable utility functions and a custom API wrapper class designed to support the Bitcoin price forecasting pipeline using PyCaret’s time series module. It handles data fetching from CoinGecko, preprocessing, lag feature engineering, model setup, and forecasting.

---

### Logging Setup

At the top of the module, Python’s built-in `logging` library is initialized to capture detailed runtime information. The log format includes timestamps, the module name, and message level. Throughout the module, `logger.info()` and `logger.error()` statements provide visibility into key actions and errors, which helps with debugging and monitoring.

---

#### 1. Class: `CoinGeckoAPI`

This class acts as a wrapper around the CoinGecko public API. It is responsible for retrieving historical OHLC (Open, High, Low, Close) data for a specified cryptocurrency.

###### `__init__(self)`

* Initializes a persistent session using the `requests` library.
* Logs a message confirming successful session setup.

###### `get_ohlc(self, coin_id="bitcoin", vs_currency="usd", days="max")`

* Constructs a GET request to the CoinGecko endpoint that returns OHLC data for the specified `coin_id`, `vs_currency`, and time range (`days`).
* Sends the request and checks for HTTP errors using `raise_for_status()`.
* Parses the returned JSON into a Pandas DataFrame with columns: `timestamp`, `open`, `high`, `low`, and `close`.
* Converts UNIX timestamps into human-readable datetime objects and sets this as the DataFrame index.
* Logs the number of records fetched and returns the cleaned DataFrame.

This method provides a standardized, clean interface for pulling historical cryptocurrency prices in a structured format.

---

#### 2. Function: `fetch_and_validate_data(client, days=90)`

This function coordinates the process of retrieving, validating, and enriching raw Bitcoin price data.

* Calls the `get_ohlc()` method from the `CoinGeckoAPI` client for the specified time period (`days`).
* Performs data validation checks:

  * Ensures the result is a non-empty DataFrame.
  * Confirms that the necessary OHLC columns are present.
* Drops duplicate timestamps, retaining the first occurrence to maintain chronological integrity.
* Computes and adds several derived features:

  * **daily\_return**: The percentage change in closing price relative to the previous timestamp. This indicates short-term price momentum.
  * **volatility\_7d**: A rolling standard deviation of the daily returns over a 7-day window, providing insight into weekly market variability.
  * **volume\_ema\_14**: The 14-period exponential moving average of the closing price, used to highlight underlying trends while minimizing noise.

The function returns a cleaned and feature-enhanced DataFrame ready for further modeling.

---

#### 3. Function: `prepare_data_for_pycaret(data)`

This function prepares the dataset in a format compatible with PyCaret’s time series requirements.

* Selects only the `close` column from the input DataFrame, which is the target variable for forecasting.
* Converts the data to a daily frequency using `.asfreq('D')`, ensuring that every day has an entry.
* Applies forward fill (`ffill`) to handle any missing days by copying the previous day’s value.

This process results in a regularly spaced time series, which is essential for most time series algorithms.

---

#### 4. Function: `run_pycaret_experiment(data)`

This function sets up a time series forecasting experiment using PyCaret.

* Validates that the DataFrame has a `DatetimeIndex`, which is mandatory for time series analysis.
* Filters to retain only numeric columns and drops rows with missing values.
* Calls `pycaret.time_series.setup()` with the following parameters:

  * `data`: the cleaned time series data.
  * `target`: the column to forecast, in this case, `close`.
  * `fold_strategy`: set to `expanding`, which progressively increases the training window.
  * `fold`: number of cross-validation folds (set to 3).
  * `numeric_imputation_target`: specifies how to handle missing target values (uses forward fill).
  * `session_id`: sets a fixed random seed for reproducibility.
  * `fh`: the forecast horizon, here set to 7 (i.e., predicting the next 7 time steps).
  * `verbose`: enables detailed setup logs for transparency.

The function returns the PyCaret experiment object, allowing further actions like model comparison and prediction.

---

#### 5. Function: `forecast_best_model()`

This function automates model selection, final training, and future forecasting.

* Calls `compare_models()`, which evaluates a variety of time series models and selects the one with the best cross-validation performance based on default metrics like MAE or RMSE.
* Finalizes the best model using `finalize_model()`, which retrains the model on the entire dataset (not just training folds).
* Generates predictions for the next 7 time periods using `predict_model()` on the finalized model.

The function returns both the best model object and the future predictions as a DataFrame. This enables users to understand which model was chosen and view its near-term forecasts.

---

#### 6. Function: `add_lag_features(df, lags=[1, 2, 3])`

This function adds lag features to the dataset, which are often used in auto-regressive forecasting models.

* Accepts a DataFrame (`df`) and a list of lags (e.g., `[1, 2, 3]`).
* For each lag `n` in the list, a new column `lag_n` is created by shifting the `close` column by `n` time steps backward.

  * For example, `lag_1` contains the closing price from one day ago, `lag_2` from two days ago, etc.
* These features provide the model with access to past observations, which can improve its ability to capture temporal dependencies and make accurate predictions.
* After adding lag features, the function drops rows with missing values caused by the shifting process (e.g., the first few rows).

It returns the DataFrame with new lag-based columns, cleaned of null entries.

---

# Summary

The `PyCaret_utils.py` module abstracts and organizes the core functionalities needed for time series forecasting using PyCaret:

* **`CoinGeckoAPI`** fetches clean OHLC data from CoinGecko.
* **`fetch_and_validate_data`** processes and enriches the time series.
* **`prepare_data_for_pycaret`** formats the data for PyCaret compatibility.
* **`run_pycaret_experiment`** configures and initializes a time series experiment.
* **`forecast_best_model`** selects, finalizes, and forecasts with the best model.
* **`add_lag_features`** introduces auto-regressive features for enhanced learning.

