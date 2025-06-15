# BTC_SQLAlchemy.API.md

## Overview

This document explains the architecture and software layer built on top of the native CoinGecko API. The wrapper layer is implemented in the `BTC_SQLAlchemy_utils.py` module. It simplifies the process of fetching, storing, and accessing real-time Bitcoin price data using SQLAlchemy ORM.

---

## Native API: CoinGecko

We use CoinGecko's public REST API to fetch Bitcoin price data. The following endpoints are used:

1. **Current Price**
   - Endpoint: `https://api.coingecko.com/api/v3/simple/price`
   - Returns the latest Bitcoin price in USD.

2. **Historical Price Series**
   - Endpoint: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart`
   - Returns hourly Bitcoin prices for the past 30 days.

These responses are in JSON format and are parsed in our wrapper functions.

---

## Wrapper Layer: `BTC_SQLAlchemy_utils.py`

To abstract the API and database operations, we implemented the following functions:

### Database Setup

- `init_db()`  
  Initializes a SQLite database and creates the `bitcoin_prices` table if it does not exist.

- `get_session(engine)`  
  Creates a SQLAlchemy session for database transactions.

### Data Fetching

- `fetch_price()`  
  Fetches the current Bitcoin price (real-time snapshot).

- `fetch_30day_price_series()`  
  Fetches historical hourly prices for the past 30 days.

- `fetch_realtime_5min_series(interval_seconds=15)`  
  Fetches live Bitcoin prices every few seconds over a 5-minute window.

### Data Storage

- `save_price(session, price)`  
  Inserts a single timestamped price into the database.

- `save_price_series(session, price_list)`  
  Inserts a batch of prices into the database, skipping duplicates.

### Data Access

- `load_data_from_db()`  
  Loads all stored Bitcoin prices from the database as a pandas DataFrame, indexed and sorted by timestamp.

---

## Design Decisions

- **ORM with SQLAlchemy**  
  We use SQLAlchemy's declarative base to define the database schema, improving maintainability and avoiding raw SQL.

- **Data deduplication**  
  When inserting multiple records, the `save_price_series()` function checks for existing timestamps and skips duplicates to preserve database integrity.

- **Separation of concerns**  
  API and database logic is encapsulated in reusable utility functions to keep notebooks clean and maintainable.

- **Real-time ingestion**  
  Live data is captured with custom intervals using the 5-minute streaming function, enabling both static and dynamic modeling.

---

## Conclusion

This API layer provides a clean, reusable, and extensible interface for working with real-time and historical Bitcoin price data. It simplifies interaction with external services and local databases, forming the backbone of our analysis and modeling pipeline.
