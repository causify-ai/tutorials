import os
import time
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from logger_config import setup_logger

logger = setup_logger('btc_fetcher')

def fetch_and_store():
    influxdb_url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
    influxdb_token = os.getenv('INFLUXDB_TOKEN')
    influxdb_org = os.getenv('INFLUXDB_ORG')
    influxdb_bucket = os.getenv('INFLUXDB_BUCKET')
    fsym = os.getenv('FETCH_FSYM', 'BTC')
    tsym = os.getenv('FETCH_TSYM', 'USD')
    
    logger.info(f"Fetching {fsym}/{tsym} data...")

    try:
        url = 'https://min-api.cryptocompare.com/data/v2/histominute'
        params = {'fsym': fsym, 'tsym': tsym, 'limit': 60}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()['Data']['Data']

        with InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)

            # Write historical data points
            for entry in data:
                historical_point = Point("crypto_prices") \
                    .tag("fsym", fsym) \
                    .tag("tsym", tsym) \
                    .tag("source", "historical") \
                    .field("open", float(entry["open"])) \
                    .field("high", float(entry["high"])) \
                    .field("low", float(entry["low"])) \
                    .field("close", float(entry["close"])) \
                    .field("volume", float(entry["volumefrom"])) \
                    .field("volume_to", float(entry["volumeto"])) \
                    .time(entry["time"], write_precision="s")
                write_api.write(bucket=influxdb_bucket, record=historical_point)

            # Write real-time data point using the latest entry
            latest = data[-1]
            realtime_point = Point("crypto_prices") \
                .tag("fsym", fsym) \
                .tag("tsym", tsym) \
                .tag("source", "realtime") \
                .field("open", float(latest["open"])) \
                .field("high", float(latest["high"])) \
                .field("low", float(latest["low"])) \
                .field("close", float(latest["close"])) \
                .field("volume", float(latest["volumefrom"])) \
                .field("volume_to", float(latest["volumeto"])) \
                .time(latest["time"], write_precision="s")
            write_api.write(bucket=influxdb_bucket, record=realtime_point)

        logger.info(f"Wrote {len(data)} historical points and 1 realtime point to InfluxDB [bucket: {influxdb_bucket}]")

    except Exception as e:
        logger.error(f"Error during fetch and store: {str(e)}")
        raise

def main():
    FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 10))
    logger.info(f"Starting BTC price fetcher (interval: {FETCH_INTERVAL}s)")

    while True:
        try:
            fetch_and_store()
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
