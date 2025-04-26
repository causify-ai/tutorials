import time
import requests
from collections import deque
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# === SETTINGS ===
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
FETCH_INTERVAL = 30  # seconds
WINDOW_SIZE = 10     # Moving average over last 10 prices

# === INFLUXDB SETTINGS ===
INFLUXDB_URL = "http://influxdb_container:8086"
INFLUXDB_TOKEN = "97CizutSicLf2emH0e3s584dTMCqNitFav4Nl4fMeXdu4IW9f7D28oll8OnP4Q1fEd8QESBShjv_o7pLnw05Ew=="
INFLUXDB_ORG = "crypto"
INFLUXDB_BUCKET = "bitcoin_prices"

# === SETUP ===
price_window = deque(maxlen=WINDOW_SIZE)

# Connect to InfluxDB
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG,
    timeout=30000,
)

write_api = client.write_api(write_options=SYNCHRONOUS)

print("\nStreaming real Bitcoin prices and writing to InfluxDB...\n")

while True:
    try:
        # Fetch Bitcoin price
        response = requests.get(API_URL, timeout=10)
        data = response.json()

        if "bitcoin" in data and "usd" in data["bitcoin"]:
            price = data["bitcoin"]["usd"]
            current_time = datetime.utcnow()

            # Add price to window
            price_window.append(price)

            print(f"[{current_time}] Current Price: ${price}")
            
            # Write current price to InfluxDB
            point = (
                Point("bitcoin_price")
                .field("price", price)
                .time(current_time)
            )
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)

            # Write moving average if enough data
            if len(price_window) == WINDOW_SIZE:
                moving_avg = sum(price_window) / WINDOW_SIZE
                print(f"-----> Moving Average of last {WINDOW_SIZE} prices: ${moving_avg:.2f}\n")

                moving_avg_point = (
                    Point("bitcoin_moving_avg")
                    .field("moving_average", moving_avg)
                    .time(current_time)
                )
                write_api.write(bucket=INFLUXDB_BUCKET, record=moving_avg_point)

        else:
            print(f"API error: Unexpected response -> {data}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"Error while processing: {e}")

    # Sleep before next fetch
    print(f"Waiting for {FETCH_INTERVAL} seconds...\n")
    time.sleep(FETCH_INTERVAL)
