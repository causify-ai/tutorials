# docker_sdk_utils.py

import os
import logging
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import docker
import time
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docker_sdk_utils")

# Check for required environment variables
# required_env = [
#     "INFLUXDB_USERNAME", "INFLUXDB_PASSWORD", "INFLUXDB_ORG",
#     "INFLUXDB_BUCKET", "INFLUXDB_ADMIN_TOKEN", "INFLUXDB_URL"
# ]
# for var in required_env:
#     if not os.getenv(var):
#         raise RuntimeError(f"Missing required environment variable: {var}")

# ---------- DOCKER SDK FUNCTIONS ----------

def list_docker_images():
    client = docker.from_env()
    return client.images.list()

def list_docker_containers(all=True):
    client = docker.from_env()
    return client.containers.list(all=all)

def pull_docker_image(image_name):
    client = docker.from_env()
    return client.images.pull(image_name)

def start_influxdb_container(client, container_name="influxdb", port=8086):
    logger.info("Starting InfluxDB container...")

    container = client.containers.run(
        image="influxdb:2.7",
        name=container_name,
        ports={"8086/tcp": port},
        environment={
            "DOCKER_INFLUXDB_INIT_MODE": "setup",
            "DOCKER_INFLUXDB_INIT_USERNAME": os.getenv("INFLUXDB_USERNAME"),
            "DOCKER_INFLUXDB_INIT_PASSWORD": os.getenv("INFLUXDB_PASSWORD"),
            "DOCKER_INFLUXDB_INIT_ORG": os.getenv("INFLUXDB_ORG"),
            "DOCKER_INFLUXDB_INIT_BUCKET": os.getenv("INFLUXDB_BUCKET"),
            "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": os.getenv("INFLUXDB_ADMIN_TOKEN"),
        },
        detach=True,
        network="btc-net",  # <-- UNCOMMENT THIS
        auto_remove=False
    )

    # Allow time for container to initialize and log status
    time.sleep(2)
    container.reload()
    logger.info(f"InfluxDB container status: {container.status}")

    return container

def stop_docker_container(container_name):
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        container.stop(timeout=3)
        time.sleep(2)
        container.remove(force=True)
        return True
    except docker.errors.NotFound:
        logger.warning(f"Container {container_name} not found.")
        return False
    except docker.errors.APIError as e:
        logger.warning(f"Skipping removal of {container_name} due to Docker API conflict: {e}")
        return False

# ---------- BTC DATA FETCHER ----------

class CryptoDataFetcher:
    def __init__(self, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket):
        self.influxdb_url = influxdb_url
        self.influxdb_token = influxdb_token
        self.influxdb_org = influxdb_org
        self.influxdb_bucket = influxdb_bucket

        self._log = logging.getLogger(self.__class__.__name__)

    def fetch_histominute(self, fsym: str, tsym: str, limit: int = 60):
        url = 'https://min-api.cryptocompare.com/data/v2/histominute'
        params = {'fsym': fsym, 'tsym': tsym, 'limit': limit}
        self._log.info("Fetching historical minute data for %s/%s", fsym, tsym)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            json_data = response.json()
        except Exception as e:
            self._log.error("HTTP request failed or JSON decode failed: %s", e)
            return

        if json_data.get("Response") == "Error":
            self._log.error("API returned an error: %s", json_data.get("Message"))
            return

        try:
            with InfluxDBClient(url=self.influxdb_url, token=self.influxdb_token, org=self.influxdb_org) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                for entry in json_data["Data"]["Data"]:
                    point = Point("crypto_prices") \
                        .tag("fsym", fsym) \
                        .tag("tsym", tsym) \
                        .field("open", float(entry["open"])) \
                        .field("high", float(entry["high"])) \
                        .field("low", float(entry["low"])) \
                        .field("close", float(entry["close"])) \
                        .field("volume", float(entry["volumefrom"])) \
                        .field("volume_to", float(entry["volumeto"])) \
                        .time(entry["time"], write_precision="s")
                    write_api.write(bucket=self.influxdb_bucket, record=point)
                self._log.info("Data written to InfluxDB for %s/%s", fsym, tsym)
        except Exception as e:
            self._log.error("Failed to write data to InfluxDB: %s", e)

    def query_data(self, start="-60m"):
        from influxdb_client import InfluxDBClient
        query = f'from(bucket: "{self.influxdb_bucket}") |> range(start: {start}) |> filter(fn: (r) => r._measurement == "crypto_prices")'
        try:
            with InfluxDBClient(url=self.influxdb_url, token=self.influxdb_token, org=self.influxdb_org) as client:
                tables = client.query_api().query(query, org=self.influxdb_org)
                data = []
                for table in tables:
                    for record in table.records:
                        data.append({
                            "time": record.get_time(),
                            "field": record.get_field(),
                            "value": record.get_value(),
                            "fsym": record.values.get("fsym"),
                            "tsym": record.values.get("tsym")
                        })
                return data
        except Exception as e:
            self._log.error("Failed to query InfluxDB: %s", e)
            return []
        
    def time_series_analysis(self, df, order=(1,1,1), window=5):
        """
        Perform moving average and ARIMA analysis on a DataFrame of BTC prices.
        :param df: DataFrame with 'time' and 'value' columns (close prices)
        :param order: ARIMA order tuple
        :param window: Window size for moving average
        :return: DataFrame with moving average and ARIMA forecast
        """
        result = df.copy()
        result['moving_avg'] = result['value'].rolling(window=window).mean()
        # Fit ARIMA model
        try:
            model = ARIMA(result['value'], order=order)
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=5)
            # Append forecast as new rows
            forecast_df = pd.DataFrame({
                'time': pd.date_range(start=result['time'].iloc[-1], periods=6, freq='T')[1:],
                'value': [None]*5,
                'moving_avg': [None]*5,
                'arima_forecast': forecast.values
            })
            result['arima_forecast'] = None
            result = pd.concat([result, forecast_df], ignore_index=True)
        except Exception as e:
            self._log.error(f"ARIMA model failed: {e}")
            result['arima_forecast'] = None
        return result

# -- Grafana container helpers --
def start_grafana_container(container_name='grafana', port=3000, network=None):
    client = docker.from_env()
    # Remove any old instance
    try:
        client.containers.get(container_name).remove(force=True)
    except docker.errors.NotFound:
        pass
    # Mount provisioning configs for datasources and dashboards
    project_dir = os.path.abspath(os.path.dirname(__file__))
    datasources_dir = os.path.join(project_dir, 'grafana-provisioning', 'datasources')
    dashboards_dir = os.path.join(project_dir, 'grafana-provisioning', 'dashboards')
    return client.containers.run(
        'grafana/grafana',
        name=container_name,
        ports={'3000/tcp': port},
        volumes={
            datasources_dir: {'bind': '/etc/grafana/provisioning/datasources', 'mode': 'ro'},
            dashboards_dir: {'bind': '/etc/grafana/provisioning/dashboards', 'mode': 'ro'}
        },
        detach=True,
        network=network
    )

def stop_grafana_container(container_name='grafana'):
    client = docker.from_env()
    try:
        c = client.containers.get(container_name)
        c.stop()
        c.remove()
    except docker.errors.NotFound:
        pass

# -- BTC Fetcher job container launcher --
def start_btc_fetcher_container(
    container_name='btc-fetcher', image_name='bitcoin_realtime_sdk', fsym='BTC', tsym='USD', limit=60, network=None
):
    client = docker.from_env()
    env_vars = {
        'INFLUXDB_URL': os.environ["INFLUXDB_URL"],
        'INFLUXDB_TOKEN': os.environ["INFLUXDB_ADMIN_TOKEN"],
        'INFLUXDB_ORG': os.environ["INFLUXDB_ORG"],
        'INFLUXDB_BUCKET': os.environ["INFLUXDB_BUCKET"],
        'FETCH_FSYM': fsym,
        'FETCH_TSYM': tsym,
        'FETCH_LIMIT': str(limit)
    }
    # Remove old container if exists
    try:
        client.containers.get(container_name).remove(force=True)
    except docker.errors.NotFound:
        pass
    container = client.containers.run(
        image_name,
        name=container_name,
        command=["python", "fetch_btc_data.py"],
        environment=env_vars,
        network=network,
        detach=True
    )
    logger.info(f"Started BTC fetcher container '{container_name}' in detached mode. Logs will stream below:")
    for log in container.logs(stream=True):
        logger.info(log.decode().strip())
    return container

def wait_for_influxdb_ready(url="http://influxdb:8086", timeout=120):
    logger.info("Waiting for InfluxDB to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url + "/health", timeout=5)
            logger.info(f"InfluxDB /health status: {response.status_code}, body: {response.text}")
            if response.status_code == 200 and "pass" in response.text:
                logger.info("InfluxDB is ready.")
                return
        except requests.exceptions.RequestException as e:
            logger.debug(f"Health check connection failed: {e}")
        time.sleep(3)
    raise TimeoutError("InfluxDB did not become ready in time.")