# Bitcoin Market Data Analysis with SQLite & CoinMarketCap API

This Jupyter notebook provides a robust and reproducible workflow for analyzing both historical and live Bitcoin (BTC-USD) market data. Leveraging Python, SQLite, and public APIs, it demonstrates best practices in data retrieval, storage, querying, and real-time updates.

---

## **Notebook Objectives**

- Fetch and analyze 15 years of daily historical Bitcoin price and volume data.
- Store and manage data efficiently using a local SQLite database.
- Retrieve and display live Bitcoin market data from CoinMarketCap.
- Update the database with the latest live data points.
- Ensure transparency and maintainability through clear code documentation and section-wise explanations.

---

## **Notebook Structure**

| Section                    | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| **Setup and Imports**      | Initialize environment, import libraries, and configure notebook extensions.|
| **API Configuration**      | Set up API keys, endpoints, and request parameters for CoinMarketCap.      |
| **Historical Data Retrieval** | Fetch and inspect 15 years of daily BTC-USD historical data.           |
| **Data Storage**           | Persist historical data in a local SQLite database.                        |
| **Database Querying**      | Retrieve and analyze stored data using SQL queries.                        |
| **Live Data Fetching**     | Obtain the latest Bitcoin market data from CoinMarketCap.                  |
| **Database Update**        | Append new live data points to the SQLite database.                        |
| **Verification**           | Confirm successful updates and review the latest records in the database.  |

---

## **Key Features**

- **Comprehensive Data Pipeline**: From historical data ingestion to live updates and persistent storage.
- **Reproducibility**: All steps are documented and organized for clarity.
- **Extensibility**: Modular code structure allows easy adaptation for other cryptocurrencies or data sources.
- **Visualization Ready**: Data is formatted and stored for downstream analysis and visualization.

---

## **Usage Instructions**

1. **Environment Setup**: Ensure you have Python 3.x and the following packages installed:
   - `pandas`, `requests`, `sqlite3`, `mplfinance`, `yfinance`, `matplotlib`, `seaborn`
2. **API Key**: Insert your CoinMarketCap API key in the designated section.
3. **Run Notebook**: Execute each cell in order for a seamless data pipeline from retrieval to storage and live updates.

---

## Tool API Reference

| Function             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `fetchHistoricalBTC()` | Retrieves 15 years of BTC-USD data using `yfinance`.                        |
| `storeData()`           | Inserts a DataFrame into the SQLite database.                              |
| `fetchDB()`             | Executes a custom SQL query and returns a DataFrame.                       |
| `liveBTC()`             | Fetches the latest BTC data from CoinMarketCap.                            |
| `addDatapoint()`        | Appends the live data into the SQLite database.                            |

---

## Quickstart Examples

### 1. Fetch Historical Data
```python
# Retrieve data as DataFrame
df = fetchHistoricalBTC('BTC-USD', period='15y', interval='1d')
print(df.head())
```

### 2. Insert into SQLite Database
```python
# Save fetched data into DB
storeData(df, 'btcDaily.db')
```

### 3. Query the Database
```python
# Custom SQL query
result = fetchDB("SELECT * FROM btc_daily_stats WHERE close > 30000", 'btcDaily.db')
print(result.head())
```

### 4. Fetch Latest Live Data
```python
# Retrieve live BTC data
url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
API_KEY = "<your_key>"
live_data, _ = liveBTC(url, API_KEY)
print(live_data)
```

### 5. Update Database with Live Data
```python
# Add latest live BTC data to DB
addDatapoint(live_data, 'btcDaily.db')
```

---

## Function Signatures

### `fetchHistoricalBTC(ticker, period, interval)`
- **Returns**: `pd.DataFrame` with historical BTC data.
- **Columns**: `['date', 'close', 'high', 'low', 'open', 'volume']`

### `storeData(data, db)`
- **Arguments**: `data` — DataFrame with BTC market data; `db` — DB file path.
- **Effect**: Inserts data into the `btc_daily_stats` table.

### `fetchDB(query, db)`
- **Arguments**: `query` — SQL string; `db` — DB file path.
- **Returns**: Query result as a `pd.DataFrame`.

### `liveBTC(url, API_KEY)`
- **Returns**: Tuple — dictionary of selected fields and raw response dictionary.
- **Source**: CoinMarketCap API

### `addDatapoint(liveData, db)`
- **Effect**: Adds the latest BTC data into the `btc_daily_stats` table.

---

## Requirements
Make sure you have the following installed:
- `pandas`, `requests`, `sqlite3`, `yfinance`, `matplotlib`, `seaborn`, `mplfinance`

---

## References
- [CoinMarketCap API Docs](https://coinmarketcap.com/api/documentation/v1/)
- [SQLite Python Docs](https://docs.python.org/3/library/sqlite3.html)

---

## **Data Overview**

- **Historical Data**: 15 years of daily BTC-USD prices and volumes, stored in `btcDaily.db` SQLite database.
- **Live Data**: Real-time Bitcoin statistics (price, volume, market cap, etc.) fetched via CoinMarketCap API and appended to the database.

---

## **Notebook Best Practices**

- All code sections are clearly labeled and commented.
- Data is validated after each major operation (fetch, store, update).
- Notebook structure is inspired by established data science best practices for clarity and reproducibility.

---