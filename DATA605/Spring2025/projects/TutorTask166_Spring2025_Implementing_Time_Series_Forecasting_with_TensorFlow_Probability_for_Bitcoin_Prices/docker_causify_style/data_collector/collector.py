import pandas as pd
import os
import logging
import json
from datetime import datetime
import time
import yaml
import csv
import asyncio
import websockets
from utilities.price_format import normalize_price
from utilities.timestamp_format import to_iso8601
from kafka import KafkaProducer

# Load config
CONFIG_PATH = '/app/configs/config.yaml'
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)
TIMESTAMP_FORMAT = config['data_format']['timestamp']['format']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add robust timestamp conversion
def safe_iso8601(ts):
    # If ts is a float/int, treat as epoch
    if isinstance(ts, (int, float)):
        # Validate reasonable range (2000-01-01 to 2100-01-01)
        if ts < 946684800 or ts > 4102444800:
            raise ValueError(f"Timestamp {ts} out of range")
        return datetime.utcfromtimestamp(ts).strftime(TIMESTAMP_FORMAT)
    # If already string, try to parse and reformat
    try:
        dt = pd.to_datetime(ts, utc=True)
        return dt.strftime(TIMESTAMP_FORMAT)
    except Exception:
        raise ValueError(f"Unrecognized timestamp: {ts}")

# Robust save_data function (as before)
def save_data(data, file_path):
    try:
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data:
                data[col] = data.get('price', 0)
        # Use robust timestamp conversion
        data['timestamp'] = safe_iso8601(data['timestamp'])
        df = pd.DataFrame([data], columns=required_columns)
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a' if os.path.exists(file_path) else 'w') as f:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                if f.tell() == 0:
                    df.to_csv(f, index=False)
                else:
                    df.to_csv(f, mode='a', header=False, index=False)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        logger.info(f"Saved data to {file_path}")
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise

class BitcoinDataCollector:
    def __init__(self, config):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config['kafka']['bootstrap_servers'],
            value_serializer=lambda x: json.dumps(x).encode()
        )
        self.data_file = os.path.join('/app/data', 'raw/instant_data.csv')

    def publish_to_kafka(self, bar):
        self.producer.send(self.config['kafka']['topic'], bar)
        self.producer.flush()
        logger.info(f"→ pushed to Kafka: {bar}")

    async def stream_1s_ohlc(self):
        uri = "wss://ws-feed.exchange.coinbase.com"
        curr_sec = None
        o = h = l = c = v = None
        while True:
            try:
                async with websockets.connect(uri, ping_interval=20) as ws:
                    subscribe_msg = {
                        "type": "subscribe",
                        "channels": [{"name": "ticker", "product_ids": ["BTC-USD"]}]
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    async for message in ws:
                        msg = json.loads(message)
                        if msg.get("type") != "ticker":
                            continue
                        ts = datetime.fromisoformat(msg["time"].replace("Z", "+00:00"))
                        price = float(msg["price"])
                        size = float(msg.get("last_size", 0.0))
                        sec = int(ts.timestamp())
                        if curr_sec is None:
                            curr_sec = sec
                            o = h = l = c = price
                            v = size
                        elif sec == curr_sec:
                            h = max(h, price)
                            l = min(l, price)
                            c = price
                            v += size
                        else:
                            # Flush the completed second to CSV and Kafka
                            try:
                                row_ts = safe_iso8601(curr_sec)
                            except Exception as e:
                                logger.error(f"Skipping row due to bad timestamp: {curr_sec} ({e})")
                                curr_sec = sec
                                o = h = l = c = price
                                v = size
                                continue
                            bar = {
                                'timestamp': row_ts,
                                'open': normalize_price(o),
                                'high': normalize_price(h),
                                'low': normalize_price(l),
                                'close': normalize_price(c),
                                'volume': v
                            }
                            save_data(bar, self.data_file)
                            self.publish_to_kafka(bar)
                            logger.info(f"[System Time: {datetime.now().strftime(TIMESTAMP_FORMAT)}] Collected data for [Data Time: {row_ts}] - O={o}, H={h}, L={l}, C={c}, V={v}")
                            # Start a new bar
                            curr_sec = sec
                            o = h = l = c = price
                            v = size
            except (websockets.ConnectionClosed, asyncio.TimeoutError) as e:
                logger.warning(f"WebSocket disconnected: {e}. Reconnecting in 5s…")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}. Restarting in 5s…")
                await asyncio.sleep(5)

def main():
    logger.info(f"Starting real-time Coinbase OHLCV collector for BTC-USD")
    collector = BitcoinDataCollector(config)
    asyncio.run(collector.stream_1s_ohlc())

if __name__ == "__main__":
    main() 