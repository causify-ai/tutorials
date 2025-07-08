# API Documentation: QlikAnalysis_utils.py

This document describes the **Python API** and custom software layer developed for real-time Bitcoin data analysis and automation. The API is implemented in `QlikAnalysis_utils.py` and provides all the core functions for fetching, processing, and managing Bitcoin price data and related analytics.

---

## API Overview

The API offers a modular, reusable interface for:
- Real-time Bitcoin price collection from public APIs
- Data enrichment (moving average, volatility, forecasting)
- Automated CSV management and GitHub integration

Scripts and notebooks should interact only through these API functions.

---

## Module: QlikAnalysis_utils.py

### 1. Data Initialization and Collection

#### `initialize_csv_file(filepath: str) -> None`
Initializes a CSV file with headers (`timestamp`, `price_usd`) if it does not exist.

**Arguments:**
- `filepath` (*str*): Path to the CSV file.

---

#### `fetch_bitcoin_price() -> Optional[dict]`
Fetches the current Bitcoin price in USD from CoinGecko, with a local timestamp.

**Returns:**
- `dict`: `{ "timestamp": str, "price_usd": float }` if successful, else `None`.

---

#### `append_to_csv(record: dict, filepath: str) -> None`
Appends a new price record to the specified CSV file.

**Arguments:**
- `record` (*dict*): Contains `timestamp` and `price_usd`.
- `filepath` (*str*): Path to the CSV file.

---

### 2. Data Analysis & Feature Engineering

#### `load_bitcoin_data(csv_path: str) -> pd.DataFrame`
Loads and preprocesses Bitcoin data from CSV (parses timestamps, sorts chronologically).

**Arguments:**
- `csv_path` (*str*): Path to the CSV file.

**Returns:**
- `pd.DataFrame`: Preprocessed DataFrame.

---

#### `add_time_series_features(df: pd.DataFrame, ma_window: int = 6, vol_window: int = 12) -> pd.DataFrame`
Adds moving average and volatility columns to the DataFrame.

**Arguments:**
- `df` (*pd.DataFrame*): Input data.
- `ma_window` (*int*): Window for moving average.
- `vol_window` (*int*): Window for volatility (std dev).

**Returns:**
- `pd.DataFrame`: DataFrame with new feature columns.

---

### 3. Forecasting

#### `forecast_bitcoin(df: pd.DataFrame, periods: int = 24, freq: str = 'h') -> Optional[pd.DataFrame]`
Uses Prophet to forecast future Bitcoin prices.

**Arguments:**
- `df` (*pd.DataFrame*): Historical data.
- `periods` (*int*): Number of future periods to predict.
- `freq` (*str*): Pandas frequency string.

**Returns:**
- `pd.DataFrame`: Forecasted values (`ds`, `yhat`, `yhat_lower`, `yhat_upper`) for future periods.

---

#### `save_dataframe(df: pd.DataFrame, csv_path: str) -> None`
Saves a DataFrame to a specified CSV file.

**Arguments:**
- `df` (*pd.DataFrame*): DataFrame to save.
- `csv_path` (*str*): Destination CSV file path.

---

### 4. Automation & GitHub Integration

#### `push_csv_files_to_github(files: List[str], repo_dir: str) -> None`
Automates git operations to add, commit, and push selected CSV files to a remote GitHub repo.

**Arguments:**
- `files` (*List[str]*): List of CSV filenames to push.
- `repo_dir` (*str*): Path of the git repository.

---

## API Usage Pattern

1. Initialize a CSV file if needed.
2. Collect and append new Bitcoin price data.
3. Analyze data and add features.
4. Forecast future prices.
5. Save results and push to GitHub for dashboard/remote access.

---

## Software Layer Structure

- **All business logic** resides in `QlikAnalysis_utils.py`.
- **Scripts and notebooks** (e.g., `datafetch.py`, `Analysis.py`) only call public API functions from the utils module.
- **No complex logic** is embedded in scripts or notebooks. All reusable code is kept in the API layer for clarity, maintainability, and reuse.

---

*For full argument types, return types, and details, see docstrings in `QlikAnalysis_utils.py`.*
