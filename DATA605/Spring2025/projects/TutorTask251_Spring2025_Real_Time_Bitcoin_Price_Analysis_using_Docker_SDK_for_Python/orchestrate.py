import os
import time
import docker
from docker.errors import NotFound
from docker_sdk_utils import (
    CryptoDataFetcher, stop_docker_container, stop_grafana_container, start_influxdb_container, start_grafana_container, start_btc_fetcher_container
)
from dotenv import load_dotenv
import logging

# Load .env file automatically
load_dotenv()

INFLUXDB_PORT = 8086
GRAFANA_PORT = 3000

# Read env vars
INFLUXDB_URL = f"http://localhost:{INFLUXDB_PORT}"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

client = docker.from_env()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrate")

def start_all():
    logger.info("Starting InfluxDB container...")
    influxdb_container = start_influxdb_container(container_name='influxdb', port=INFLUXDB_PORT)
    time.sleep(10)
    logger.info("Starting Grafana container...")
    grafana_container = start_grafana_container(container_name='grafana', port=GRAFANA_PORT)
    time.sleep(5)
    logger.info("Starting BTC fetcher container...")
    btc_fetcher = start_btc_fetcher_container(
        influxdb_url=INFLUXDB_URL,
        influxdb_token=INFLUXDB_TOKEN,
        influxdb_org=INFLUXDB_ORG,
        influxdb_bucket=INFLUXDB_BUCKET,
        container_name='btc-fetcher',
        image_name='bitcoin_realtime_sdk',
        fsym='BTC',
        tsym='USD',
        limit=60
    )
    logger.info("Waiting for BTC fetcher to finish...")
    btc_fetcher.wait()
    logger.info(btc_fetcher.logs().decode())
    logger.info("All containers started and data fetched.")
    return influxdb_container, grafana_container

def fetch_and_analyze():
    logger.info("Querying and analyzing data...")
    fetcher = CryptoDataFetcher(
        influxdb_url=INFLUXDB_URL,
        influxdb_token=INFLUXDB_TOKEN,
        influxdb_org=INFLUXDB_ORG,
        influxdb_bucket=INFLUXDB_BUCKET
    )
    data = fetcher.query_data(start="-60m")
    if data:
        import pandas as pd
        import matplotlib.pyplot as plt
        df = pd.DataFrame(data)
        close_prices = df[df['field']=='close'][['time', 'value']].sort_values('time')
        ts_df = fetcher.time_series_analysis(close_prices.reset_index(drop=True), order=(1,1,1), window=5)
        plt.figure(figsize=(10,4))
        plt.plot(ts_df['time'], ts_df['value'], label='Close Price')
        plt.plot(ts_df['time'], ts_df['moving_avg'], label='Moving Avg (5)')
        if ts_df['arima_forecast'].notnull().any():
            plt.plot(ts_df['time'], ts_df['arima_forecast'], label='ARIMA Forecast', linestyle='--')
        plt.title('BTC/USD Close Price: Moving Avg & ARIMA')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        logger.info("No data found in InfluxDB.")

def cleanup_all():
    logger.info("Stopping and removing InfluxDB and Grafana containers...")
    stop_docker_container('influxdb')
    stop_grafana_container('grafana')
    logger.info("Cleanup complete.")

def main():
    influxdb_container, grafana_container = start_all()
    fetch_and_analyze()
    input("Press Enter to clean up containers...")
    cleanup_all()

if __name__ == "__main__":
    main()
