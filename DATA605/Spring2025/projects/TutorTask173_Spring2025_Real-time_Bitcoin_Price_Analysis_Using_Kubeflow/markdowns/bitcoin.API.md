# bitcoin.API.md

## Project Scope
This project captures real-time Bitcoin prices using the CoinGecko API, 
stores them in a TimescaleDB database, and provides visualization and 
forecasting capabilities. The system is containerized using Docker and 
optionally integrated with Kubeflow Pipelines to automate recurring runs.

## Native API: CoinGecko

- Base URL: `https://api.coingecko.com/api/v3/simple/price`
- Parameters:
  - `ids`: bitcoin
  - `vs_currencies`: usd
- Response: JSON with current Bitcoin price in USD

## Software Layer (Python Wrapper)

Implemented in `bitcoin_utils.py`, the wrapper includes:
- `fetch_bitcoin_price()` - Calls the CoinGecko API
- `save_to_db(price, db_host)` - Inserts price data into TimescaleDB
- `save_to_csv(df)` - Appends each record to a CSV log

## Docker Integration

- Dockerfile installs dependencies and runs the fetcher
- Container is scheduled to run repeatedly, either via:
  - Shell script (`run_every_minute.sh`)
  - Kubeflow recurring runs

