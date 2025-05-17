# django_orm.API.md

## CoinGecko API

**Endpoint:**  
`https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`

**Description:**  
This public API endpoint returns the current market price of Bitcoin in USD. It is used to fetch real-time price data for storage and visualization in the Django web application.

---

## Wrapper Functions (in `django_orm_utils.py`)

These functions encapsulate interactions with the CoinGecko API and the Django ORM, enabling reusable, modular ingestion and retrieval logic.

---

### `get_current_bitcoin_price()`
Fetches the current Bitcoin price in USD from the CoinGecko API.  
**Returns:** `float` — the latest price value  
**Used for:** real-time data ingestion

---

### `store_price_in_db(price)`
Stores the given Bitcoin price in the `BitcoinPrice` Django model with the current timestamp.  
**Arguments:** `price` *(float)*  
**Returns:** None

---

### `fetch_and_store()`
Convenience wrapper that fetches the latest Bitcoin price and immediately stores it in the database.  
**Returns:** `float` — the stored price

---

### `get_last_n_prices(n)`
Retrieves the last `n` Bitcoin price entries from the database in chronological order.  
**Arguments:** `n` *(int)* — number of records  
**Returns:** `QuerySet` — list of `BitcoinPrice` objects

---

## Data Processing Functions (in `django_orm_utils.py`)

These helper functions process price data for time series analysis and statistical summary. They are called from the view layer and power the insights visualized on the Plotly chart.

---

### `compute_average(prices)`
Computes the arithmetic mean of a list of Bitcoin prices.  
**Arguments:** `prices` *(List[float])*  
**Returns:** `float` — average price (rounded)

---

### `compute_volatility(prices)`
Calculates the standard deviation (volatility) of a list of prices.  
**Arguments:** `prices` *(List[float])*  
**Returns:** `float` — volatility (rounded)

---

### `detect_peaks(prices)`
Detects local peaks in a price trend using `scipy.signal.find_peaks`.  
**Arguments:** `prices` *(List[float])*  
**Returns:** `List[int]` — indices of peak values in the list

---

## Quick Reference

**Wrapper Functions**
- `get_current_bitcoin_price()`
- `store_price_in_db(price)`
- `fetch_and_store()`
- `get_last_n_prices(n)`

**Data Processing**
- `compute_average(prices)`
- `compute_volatility(prices)`
- `detect_peaks(prices)`

---

## Dependencies

- `requests` — for HTTP communication with the CoinGecko API  
- `django.db.models` — for ORM-based database access  
- `numpy` — for numerical calculations (average, std)  
- `scipy.signal` — for peak detection in time series data
