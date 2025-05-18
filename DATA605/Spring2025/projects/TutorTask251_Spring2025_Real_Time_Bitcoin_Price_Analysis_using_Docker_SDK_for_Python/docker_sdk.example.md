# Example: Real-Time Bitcoin Price Analysis Pipeline

## Overview

This example demonstrates an end-to-end analytics pipeline built using Docker SDK for Python and containerized services.
We show how to:
- Launch an isolated InfluxDB database for time-series storage using Docker SDK
- Ingest real-time Bitcoin price data from the CryptoCompare API
- Store and query the data using InfluxDB
- Visualize real-time and historical price data using Grafana with source-tag filtering.

## Architecture

The architecture consists of containerized components managed via the Docker SDK:
- `InfluxDB`: a time-series database to store BTC price data
- `Grafana`: for visualizing the price data in real-time dashboards
- `BTC Fetcher`: a container that streams real-time BTC/USD price from CryptoCompare API to InfluxDB

All components are started and managed using Docker SDK through functions defined in `docker_sdk_utils.py`.

## Project Steps

1. **Start InfluxDB using Docker SDK**
    - Uses `start_influxdb_container()` from `docker_sdk_utils.py`.
2. **Configure InfluxDB Connection**
    - Based on `.env` values loaded into the script.
3. **Fetch and Store Bitcoin Data**
    - Launches a container using start_btc_fetcher_container() which continuously fetches real-time BTC/USD price data and writes to InfluxDB with a source: realtime tag.
	Historical data is fetched once during container startup and stored with source: historical.
4. **Query and Analyze Data**
    - Uses `CryptoDataFetcher` class to retrieve time-series data from InfluxDB.
5. **Visualize**
    - Saves a local plot as `output/btc_analysis.png` showing the latest price, moving average, and ARIMA forecast.
    - The Grafana dashboard at [http://localhost:3000] shows:
	- BTC/USD Close Price over time
	- Current Price (Stat Panel) auto-updating every 10 seconds
	- 5-Minute Moving Average
	- A Data Source dropdown in the dashboard allows toggling between realtime and historical views using the source tag (set during InfluxDB write).
6. **Clean Up**
    - Containers are removed using `stop_docker_container()` utilities for InfluxDB and Grafana.

## Benefits of This Approach

- **Reproducibility:** All dependencies and services are started programmatically.
- **Isolation:** No leftover data or services after analysis is done.
- **Scalability:** Can easily extend to more coins, schedule jobs, or add visualization dashboards (e.g., Grafana).

## Extending the Project

- Schedule automated fetching jobs with `apscheduler`.
- Analyze more cryptocurrencies or perform more advanced time series modeling.
- Use additional source tags (e.g., external-api, ml-forecast) to expand filtering and control views in Grafana without modifying the pipeline.

## How to Run

1. Make sure Docker is running and required environment variables are set in `.env`:
    - `INFLUXDB_ADMIN_TOKEN`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`
2. Run the pipeline using the provided shell script:
    ```bash
    ./run_pipeline.sh
    ```

This script will:
- Build the Docker image for the BTC fetcher (`bitcoin_realtime_sdk`)
- Automatically launch all containers (InfluxDB, Grafana, BTC Fetcher) via the Python script
3. View the dashboard at:
    ```
    http://localhost:3000
    ```

The notebook `docker_sdk.example.ipynb` replicates this process step-by-step in an interactive environment.

## Time Series Analysis (Moving Average & ARIMA)

We use pandas to compute a rolling 5-minute moving average, which is visualized in Grafana. Forecasting was removed to focus on real-time and historical visual analysis through the dashboard.

This provides a foundation for more advanced analytics and forecasting.

---

For more details, see [docker_sdk_utils.py](./docker_sdk_utils.py) and the project README.