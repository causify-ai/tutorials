import logging
import requests
import json
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from apscheduler.schedulers.blocking import BlockingScheduler

class CryptoDataFetcher:
    def __init__(self, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket):
        # Initialize InfluxDB configuration
        self.influxdb_url = influxdb_url
        self.influxdb_token = influxdb_token
        self.influxdb_org = influxdb_org
        self.influxdb_bucket = influxdb_bucket

        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self._log = logging.getLogger(self.__class__.__name__)

    def fetch_histominute(self, fsym: str, tsym: str, limit: int = 60) -> None:
        """
        Fetch historical minute-level data from CryptoCompare API and insert into InfluxDB.

        :param fsym: Base cryptocurrency symbol (e.g., 'BTC')
        :param tsym: Quote currency symbol (e.g., 'USD')
        :param limit: Number of minutes of data to retrieve (default 60)
        """
        url = 'https://min-api.cryptocompare.com/data/v2/histominute'
        params = {'fsym': fsym, 'tsym': tsym, 'limit': limit}
        self._log.info("Fetching historical minute data for %s/%s", fsym, tsym)

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self._log.error("HTTP request failed: %s", e)
            return

        try:
            json_data = response.json()
        except json.JSONDecodeError as e:
            self._log.error("Failed to decode JSON response: %s", e)
            return

        if json_data.get("Response") == "Error":
            error_message = json_data.get("Message", "Unknown error")
            self._log.error("API returned an error: %s", error_message)
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
                self._log.info("Data successfully written to InfluxDB for %s/%s", fsym, tsym)
        except Exception as e:
            self._log.error("Failed to write data to InfluxDB: %s", e)

    def scheduled_task(self):
        """
        Task to fetch and insert data into InfluxDB every 5 minutes.
        """
        try:
            self._log.info("Running scheduled task to fetch and insert data.")
            self.fetch_histominute(fsym="BTC", tsym="USD", limit=5)
            self._log.info("Scheduled task completed successfully.")
        except Exception as e:
            self._log.error("Error occurred during scheduled task: %s", e)

    def start_scheduler(self):
        """
        Start the scheduler to run the task every 5 minutes.
        """
        scheduler = BlockingScheduler()
        scheduler.add_job(self.scheduled_task, "interval", minutes=5)  # Run every 5 minutes
        self._log.info("Running the first task immediately...")
        self.scheduled_task()  # Run the task immediately
        self._log.info("Starting the scheduler...")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self._log.info("Scheduler stopped.")


