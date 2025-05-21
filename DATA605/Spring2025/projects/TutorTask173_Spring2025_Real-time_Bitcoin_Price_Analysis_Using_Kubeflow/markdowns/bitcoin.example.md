# bitcoin.example.md

## Objective
To demonstrate an end-to-end application that collects real-time Bitcoin 
prices, stores them, and performs time series forecasting.

## Step 1: Data Collection

- Python script `fetch_bitcoin_price.py` collects data from CoinGecko.
- Output is stored in:
  - PostgreSQL/TimescaleDB
  - CSV file for historical reference

## Step 2: Data Retrieval and Visualization

- `csv_converter.py` loads the data from the database and plots 
the trend.
- It also saves the retrieved data as `bitcoin_price_log_from_db.csv`.

## Step 3: Forecasting

- `Bitcoin_TimeSeriesAnalaysis.ipynb` performs time series forecasting 
using Prophet.
- Forecasts:
  - One-year trend using historical CoinGecko data
  - Short-term trend (48 hours) using real-time collected data

## Insights

- Trend visualization reflects market consistency.
- Forecasting results demonstrate practical use of streaming data.

