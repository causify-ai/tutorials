# Bitcoin Data Analysis API Documentation

This document provides an overview of the native CoinGecko API used for fetching Bitcoin price data and the Python software layer (`CloudPickle_utils.py`) built on top of it to facilitate data ingestion, processing, and analysis.

## 1. Native API: CoinGecko

**API Name:** CoinGecko Public API  
**Endpoint Used:** `/coins/{id}/market_chart`  
**Purpose:** To fetch historical market data (price, market cap, and 24h volume) for a coin.  
**Data Format:** JSON

**Details:**
- The `/coins/bitcoin/market_chart` endpoint is used to retrieve Bitcoin's historical price data.
- **Parameters used by the wrapper:**
    - `vs_currency` (string, required): The target currency of market data (e.g., `usd`, `eur`, `jpy`). The wrapper defaults to `usd`.
    - `days` (string, required): Data up to number of days ago (e.g., `1`, `7`, `30`).
        - If `days=1`, CoinGecko returns hourly data for the last 24 hours.
        - If `days` is between 2 and 90 (inclusive), CoinGecko returns daily data by default.
        - If `days` is above 90, CoinGecko returns daily data.
        - The wrapper function `Workspace_bitcoin_price_history` reflects this behavior.
- **Authentication:** For the `/market_chart` endpoint, CoinGecko's public API is generally accessible without an API key for limited use, but it is subject to rate limits (typically 5-10 calls/minute per IP as of early 2024, subject to change). For production or higher volume usage, registering for a free API key is recommended by CoinGecko to get higher rate limits. This project's wrapper currently does not implement API key usage for simplicity, assuming basic access.
- **Rate Limiting:** Users should be mindful of the API rate limits to avoid temporary IP bans.

**Example JSON Response Snippet (prices only):**
```json
{
  "prices": [
    [1678886400000, 24500.50],
    [1678890000000, 24550.75],
    // ... more data points (timestamp in ms, price)
  ],
  "market_caps": [
    // ... market cap data
  ],
  "total_volumes": [
    // ... volume data
  ]
}
```
Each inner array in "prices" contains a Unix timestamp (in milliseconds) and the price in the specified `vs_currency`. The wrapper processes this into a Pandas DataFrame.

## 2. Python Wrapper Layer: CloudPickle_utils.py
-----------------------------------------------

The `CloudPickle_utils.py` module provides a higher-level abstraction for interacting with the CoinGecko API and performing common data analysis tasks, with a focus on using `cloudpickle` for serialization.

### Core Functionalities:

#### A. Data Ingestion:

**`Workspace_bitcoin_price_history(days=1, currency='usd')`**\
**Purpose:** Fetches Bitcoin price history from CoinGecko.\
**Input:**

-   `days` (int): Number of past days for data. `1` for hourly (last 24h), `>1` for daily.

-   `currency` (str): Target currency (default `usd`).\
    **Output:** A Pandas DataFrame with `timestamp` (as UTC datetime index) and `price` columns. Returns an empty DataFrame on error.

#### B. Data Serialization & Deserialization (with cloudpickle):

**`serialize_object(obj, filename)`**\
**Purpose:** Serializes any Python object (DataFrames, functions, models, etc.) to a file using `cloudpickle`.\
**Input:**

-   `obj` (object to serialize),

-   `filename` (str, path to save).

**`deserialize_object(filename)`**\
**Purpose:** Deserializes a Python object from a file previously saved by `cloudpickle`.\
**Input:**

-   `filename` (str, path to load from).\
    **Output:** The deserialized Python object, or None on error.

#### C. Time Series Analysis:

**`calculate_moving_average(df, window_size)`**\
**Purpose:** Calculates a simple moving average (SMA) for the `price` column.\
**Input:**

-   `df` (Pandas DataFrame with `price` column),

-   `window_size` (int, window for SMA).\
    **Output:** The DataFrame with an added column `sma_{window_size}`. Returns the original `df` or a `df` with an empty SMA column if input is invalid/empty.

**`simple_trend_analysis(df)`**\
**Purpose:** Performs a basic trend analysis by comparing the first and last price points.\
**Input:**

-   `df` (Pandas DataFrame with `price` column).\
    **Output:** A string describing the trend (e.g., "Uptrend (Change: X.XX%)").

**`plot_price_data(df, title="Bitcoin Price Analysis", columns_to_plot=None)`**\
**Purpose:** Generates and saves a plot of specified columns from the DataFrame.\
**Input:**

-   `df` (Pandas DataFrame),

-   `title` (str),

-   `columns_to_plot` (list of str, optional; defaults to `price` and existing `sma_X` columns).\
    **Output:** Filename (str) of the saved plot image (.png), or None on failure.

#### D. Multiprocessing Task Function (for use with multiprocessing module):

**`task_process_data_chunk(serialized_input_tuple)`**\
**Purpose:** A worker function designed for parallel processing. It deserializes a data chunk, a processing function, and its arguments (all passed as a cloudpickled tuple). It then applies the function to the chunk and returns the cloudpickled result.\
**Input:** A tuple `(serialized_data_chunk, serialized_processing_function, args_for_function)`.

-   `serialized_data_chunk`: `cloudpickle.dumps()` of a DataFrame chunk.

-   `serialized_processing_function`: `cloudpickle.dumps()` of a function (e.g., `calculate_moving_average`).

-   `args_for_function`: A tuple of additional arguments for the processing function (e.g., `(window_size,)`).\
    **Output:** `cloudpickle.dumps()` of the processed chunk (DataFrame), or `cloudpickle.dumps(None)` on error.

### Dependencies:

-   `requests`: For HTTP requests to CoinGecko.

-   `pandas`: For data manipulation and time series.

-   `cloudpickle`: For robust serialization of Python objects, including functions with closures, lambdas, and dynamically created classes, which is essential for distributed processing.

-   `matplotlib`: For plotting.

-   `datetime` (built-in): For handling dates and times.

-   `os` (built-in): Used in utility functions (e.g., `os.getpid()`, `os.cpu_count()`).
