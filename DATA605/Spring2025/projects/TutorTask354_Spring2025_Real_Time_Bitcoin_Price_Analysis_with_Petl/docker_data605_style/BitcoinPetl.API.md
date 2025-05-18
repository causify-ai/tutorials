# BitcoinPetl API Documentation

This document describes the utility functions in `bitcoin_petl_utils.py` for fetching and ETLing Bitcoin price data with Petl.

**Architecture & Design**

- **Layered design**:  
  1. **Fetch layer**: `fetch_btc_price_table()` hits the CoinGecko API and returns a raw Petl table.  
  2. **Demo layer**: `expand_demo_rows()` clones that single row into multi-row tables for tutorial demos.  
  3. **Filter layer**: `filter_recent()` applies time-based filters directly on Petl tables.  

- **Why Petl tables?**  
  - Consistent tabular interface for small/medium ETL tasks.  
  - Easy chaining of transforms (`convert`, `select`, etc.) without moving into pandas too early.

- **Dependencies**  
  - `requests` for HTTP  
  - `petl` for table operations  
  - Standard Python libs: `time`, `datetime`

---

## 1. `fetch_btc_price_table() -> petl.Table`

Fetch the latest Bitcoin price in USD from CoinGecko.

- **Returns**  
  A one-row PETL table with fields:
  - `timestamp` (int): UNIX epoch seconds  
  - `price_usd`  (float): price in USD  

**Example**

```python
from bitcoin_petl_utils import fetch_btc_price_table
import petl as etl

tbl = fetch_btc_price_table()
print(etl.look(tbl))
```

---

## 2. `expand_demo_rows(single_row: petl.Table, n: int = 5, dt: int = 60) -> petl.Table`

Clone a one-row table into a small multi-row table for demonstrations.

- **Parameters**  
  - `single_row`: one-row PETL table (e.g. output of `fetch_btc_price_table()`)  
  - `n`: number of rows to generate  
  - `dt`: seconds to subtract per successive row  

- **Returns**  
  A PETL table with `n` rows sorted by ascending `timestamp`.

**Example**

```python
from bitcoin_petl_utils import expand_demo_rows
demo = expand_demo_rows(tbl, n=5, dt=60)
print(etl.look(demo))
```

---

## 3. `filter_recent(table: petl.Table, lookback_min: int = 15) -> petl.Table`

Keep only rows whose `timestamp` is within the last `lookback_min` minutes.

- **Parameters**  
  - `table`: PETL table with a `timestamp` column of ints or strings  
  - `lookback_min`: lookback window in minutes  

- **Returns**  
  A filtered PETL table containing only recent rows.

**Example**

```python
from bitcoin_petl_utils import filter_recent
recent = filter_recent(demo, lookback_min=10)
print(etl.look(recent))
```