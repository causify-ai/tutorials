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

| Section                           | Description                                                                                   |
|------------------------------------|----------------------------------------------------------------------------------------------|
| **Setup and Imports**              | Initialize environment, import libraries, and configure notebook extensions.                  |
| **API Configuration**              | Set up API keys, endpoints, and request parameters for CoinMarketCap.                        |
| **Historical Data Retrieval**      | Fetch and inspect 15 years of daily BTC-USD historical data.                                 |
| **Data Storage**                   | Persist historical data in a local SQLite database.                                          |
| **Database Querying**              | Retrieve and analyze stored data using SQL queries.                                          |
| **Live Data Fetching**             | Obtain the latest Bitcoin market data from CoinMarketCap.                                    |
| **Database Update**                | Append new live data points to the SQLite database.                                          |
| **Verification**                   | Confirm successful updates and review the latest records in the database.                    |

---

## **Key Features**

- **Comprehensive Data Pipeline**: From historical data ingestion to live updates and persistent storage.
- **Reproducibility**: All steps are documented and organized for clarity.
- **Extensibility**: Modular code structure allows easy adaptation for other cryptocurrencies or data sources.
- **Visualization Ready**: Data is formatted and stored for downstream analysis and visualization.

---

## **Usage Instructions**

1. **Environment Setup**: Ensure you have Python 3.x and the following packages installed:
   - `pandas`
   - `requests`
   - `sqlite3`
   - `mplfinance`
   - `yfinance`
   - `matplotlib`
   - `seaborn`
   - Any custom utilities referenced (e.g., `sqlite_utils`)

2. **API Key**: Insert your CoinMarketCap API key in the designated section.

3. **Run Notebook**: Execute each cell in order for a seamless data pipeline from retrieval to storage and live updates.

---

## **Data Overview**

- **Historical Data**: 15 years of daily BTC-USD prices and volumes, stored in `btcDaily.db` SQLite database.
- **Live Data**: Real-time Bitcoin statistics (price, volume, market cap, etc.) fetched via CoinMarketCap API and appended to the database.

---

## **References and Further Reading**

- [SQLite3 Python Documentation](https://docs.python.org/3/library/sqlite3.html)
- [CoinMarketCap API Documentation](https://coinmarketcap.com/api/documentation/v1/)
- [Custom SQLite Utilities Documentation](sqlite.API.html)  

---

## **Notebook Best Practices**

- All code sections are clearly labeled and commented.
- Data is validated after each major operation (fetch, store, update).
- Notebook structure is inspired by established data science best practices for clarity and reproducibility.

---

