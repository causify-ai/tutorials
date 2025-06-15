


# PyCaret_utils.py Documentation

The `PyCaret_utils.py` module serves as the backbone of the time series forecasting pipeline by offering well-structured and reusable utility components. Its purpose is to streamline data acquisition, preprocessing, and feature engineering using real-time cryptocurrency price data. The module achieves this through a robust API wrapper for CoinGecko and a comprehensive data preparation function tailored to PyCaret workflows.

### Module: `PyCaret_utils.py`


## CoinGeckoAPI Class

The `CoinGeckoAPI` class encapsulates all interactions with the CoinGecko OHLC (Open, High, Low, Close) data endpoint. It initializes a session using Python’s `requests` library and optionally accepts an API key, although CoinGecko does not currently require one for public endpoints. Once initialized, users can call the `get_ohlc` method to retrieve OHLC data for any cryptocurrency supported by CoinGecko. By default, the class fetches Bitcoin data in USD for a given number of days.

The `get_ohlc` method returns a pandas DataFrame with datetime indices and the typical OHLC columns. It ensures the data is converted to a readable timestamp format and is ready for additional processing or modeling. It also includes robust error handling to catch malformed responses or connectivity issues.
##### `__init__(self, api_key=None)`

* Initializes the API client with an optional API key.
* Sets up a requests session and basic rate limiting.

##### `get_ohlc(...)`

*Fetches historical OHLC (Open, High, Low, Close) data from the CoinGecko API.

| Parameter     | Type    | Description                                |
| ------------- | ------- | ------------------------------------------ |
| `coin_id`     | str     | Cryptocurrency name (e.g., `"bitcoin"`)    |
| `vs_currency` | str     | Target currency (e.g., `"usd"`)            |
| `days`        | int/str | Number of days or `"max"` for full history |

**Returns**: `pd.DataFrame` with OHLC values and timestamp index.



## fetch_and_validate_data Function

The `fetch_and_validate_data` function acts as a wrapper around the CoinGeckoAPI instance. It combines data acquisition and transformation in a single step. First, it fetches raw OHLC data using the API wrapper. Then, it converts the data into a structured DataFrame with time-based indexing. 

Beyond simply cleaning the data, this function performs additional transformations such as computing daily returns, calculating 7-day rolling volatility, and estimating the 14-period Exponential Moving Average (EMA) of the close prices to represent smoothed volume. These derived features significantly enhance the predictive capabilities of time series models used in PyCaret or other forecasting frameworks. 

The function returns a clean and enriched DataFrame, making it immediately ready for model training and evaluation. This encapsulation ensures that the same preprocessing logic can be reused across notebooks and scripts without duplicating code.


This function performs an end-to-end process of:

1. Fetching OHLC data.
2. Validating and deduplicating the data.
3. Adding feature engineering:

   * Daily return
   * 7-day rolling volatility
   * 14-period EMA of volume

## Parameters

| Name         | Type           | Description                                |
| ------------ | -------------- | ------------------------------------------ |
| `api_client` | `CoinGeckoAPI` | API wrapper instance                       |
| `days`       | `int`          | Number of days of historical data to fetch |

**Returns**: A clean and enriched `pandas.DataFrame` ready for modeling.



##  Summary

The utilities in `PyCaret_utils.py` are responsible for:

* Abstracting API calls into a robust and reusable interface.
* Validating and preparing time series data.
* Creating derived features that enhance forecasting models.

