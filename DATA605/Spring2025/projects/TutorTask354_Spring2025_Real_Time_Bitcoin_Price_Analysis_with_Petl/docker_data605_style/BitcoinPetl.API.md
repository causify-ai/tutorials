# BitcoinPetl API Tutorial

<!-- toc -->
- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Setup & Dependencies](#setup--dependencies)
- [Fetch Layer](#fetch-layer)
- [Demo & Transformation Layer](#demo--transformation-layer)
- [Analysis Helpers](#analysis-helpers)
- [I/O Utilities](#io-utilities)
- [General Guidelines](#general-guidelines)
<!-- tocstop -->

## Introduction

The BitcoinPetl API provides a lightweight, modular ETL interface to fetch and transform real-time Bitcoin price data. Built on top of CoinGecko’s public API and the Petl library, it simplifies continuous ingestion, time series analysis, and alerting workflows.

## Architecture Overview

- **Fetch Layer**  
  - `fetch_btc_price_table()`: Retrieves the latest Bitcoin price as a one-row Petl table.  
  - `fetch_historical_range()`: Fetches historical price data over a specified UNIX timestamp range.

- **Demo & Transformation Layer**  
  - `expand_demo_rows()`: Clones a single-row table into multiple rows for demonstration.  
  - Built-in Petl operations shown in examples: `convert()`, `rename()`, `sort()`, `aggregate()`.

- **Analysis Helpers**  
  - `compute_indicators()`: Adds rolling moving average and volatility columns.  
  - `alert_on_threshold()`: Filters for price crossings above a given threshold.

- **I/O Utilities**  
  - `init_csv()`: Creates or resets a CSV file with header.  
  - `append_price()`: Appends the latest price row to CSV.  
  - `load_dataframe()`: Loads CSV into a pandas DataFrame and sets the timestamp index.  
  - `add_indicators()`: Computes and appends indicators to a DataFrame.

## Setup & Dependencies

Install required packages:

```bash
pip install requests petl pandas matplotlib seaborn statsmodels plotly
```

Imports in your notebook or script:

```python
import requests
import petl as etl
import pandas as pd
from datetime import datetime, timedelta
from bitcoin_petl_utils import (
    fetch_btc_price_table,
    fetch_historical_range,
    expand_demo_rows,
    filter_recent,
    compute_indicators,
    alert_on_threshold,
    init_csv,
    append_price,
    load_dataframe,
    add_indicators,
)
```

## Fetch Layer

### `fetch_btc_price_table() -> petl.Table`

Fetches the current BTC/USD price.

- **Returns**: Petl table with fields:
  - `timestamp` (int): UNIX epoch seconds  
  - `price_usd` (float): price in USD  

**Example**

```python
tbl = fetch_btc_price_table()
print(etl.look(tbl))
```

### `fetch_historical_range(from_ts: int, to_ts: int) -> petl.Table`

Retrieves BTC prices between UNIX timestamps.

- **Parameters**: `from_ts`, `to_ts` (seconds)  
- **Returns**: Petl table of `{timestamp, price_usd}` rows  

**Example**

```python
hist = fetch_historical_range(1620000000, 1620003600)
print(etl.look(hist))
```

## Demo & Transformation Layer

### `expand_demo_rows(single_row: petl.Table, n: int=5, dt: int=60) -> petl.Table`

Creates `n` clones of `single_row`, each offset by `dt` seconds.

- **Parameters**: `single_row`, `n`, `dt`  
- **Returns**: Sorted multi-row table  

**Example**

```python
demo = expand_demo_rows(tbl, n=5, dt=60)
print(etl.look(demo))
```

Common Petl operations demonstrated:

```python
converted = (
    demo
    .convert('timestamp', lambda t: datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'))
    .convert('price_usd', float)
    .rename('price_usd', 'price_usd_float')
    .sort('price_usd_float', reverse=True)
)
```

## Analysis Helpers

### `compute_indicators(table: petl.Table, window: int=3) -> petl.Table`

Adds `MA_{window}` and `VOL_{window}` columns.

**Example**

```python
ind_tbl = compute_indicators(tbl, window=5)
print(etl.look(ind_tbl))
```

### `alert_on_threshold(table: petl.Table, threshold: float) -> petl.Table`

Filters rows where `price_usd` ≥ `threshold`.

**Example**

```python
alerts = alert_on_threshold(tbl, 30000.0)
print(etl.look(alerts))
```

## I/O Utilities

- **`init_csv(path: str)`**: Create/reset CSV with header.  
- **`append_price(path: str)`**: Append latest price row to CSV.  
- **`load_dataframe(path: str) -> pd.DataFrame`**: Load and parse CSV into DataFrame.  
- **`add_indicators(df: pd.DataFrame, window: int=3) -> pd.DataFrame`**: Compute and append MA & volatility.