# Bitcoin.API.md

## Overview

This file documents the usage of the CoinGecko API and the custom Python utility layer implemented in `bitcoin_utils.py`. It demonstrates how real-time and historical Bitcoin pricing data is retrieved, stored, and queried using a structured and reproducible data pipeline.

The goal of this API layer is to simplify access to raw pricing data and abstract away low-level API handling, so users can focus on analysis.

---

## API Used: CoinGecko

- **Base URL**: https://api.coingecko.com/api/v3
- **Endpoints Used**:
  - `/coins/bitcoin/market_chart` - for fetching historical price data
  - `/simple/price` - for fetching real-time spot price

These endpoints return JSON responses that include timestamped price data in USD.

---

## Wrapper Functions (`bitcoin_utils.py`)

### 🔹 `fetch_historical_bitcoin_prices(days=365, interval="daily")`
- Uses the `/market_chart` endpoint
- Returns a pandas DataFrame with timestamps and prices
- Can specify number of days (default: 365)

### 🔹 `fetch_current_price()`
- Uses the `/simple/price` endpoint
- Returns a one-row DataFrame with the current price and timestamp

### 🔹 `save_to_sqlite(df, db_file, table_name="bitcoin_prices")`
- Saves any given DataFrame into a specified SQLite table
- Appends new records if the table already exists

### 🔹 `init_db()`
- Creates the SQLite database and table if they don’t exist
- Ensures the system can ingest data even on first run

---

## Design Rationale

- Using SQLite makes the project lightweight and beginner-friendly
- The abstraction layer (`bitcoin_utils.py`) ensures separation of concerns:
  - Notebooks remain readable and focused on data flow
  - Functions are modular and easy to test independently
- Jupyter notebooks invoke these wrappers to create a reproducible and interactive tutorial

---

## Dependencies

Declared in `requirements.txt`:
- `requests`, `pandas`, `sqlite3`, `matplotlib`, `schedule`, `scipy`, `statsmodels`

---

## Output

- Historical and real-time Bitcoin data is stored in:  
  `data/bitcoin_data.db` → Table: `bitcoin_prices`
- Data is ready for querying, analysis, and use in Datasette
