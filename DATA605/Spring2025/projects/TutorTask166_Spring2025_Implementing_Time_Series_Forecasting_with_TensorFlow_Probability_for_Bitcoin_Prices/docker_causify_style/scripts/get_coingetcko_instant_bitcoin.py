#!/usr/bin/env python3
"""
Bitcoin price collector using Coinbase WebSocket API.
Continuously streams BTC-USD trades and aggregates them into 1-second OHLC bars.
"""
import os
import asyncio
import json
import csv
import logging
from datetime import datetime
import websockets
import yaml
from kafka import KafkaProducer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class BitcoinDataCollector:
    def __init__(self):
        # Load configuration
        with open('/app/configs/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        self.data_file = config['data']['raw_data']['instant_data']['file']
        self.kafka_bootstrap_servers = config['kafka']['bootstrap_servers']
        self.kafka_topic = config['kafka']['topic']
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Initialize CSV file if it doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        logger.info(f"Initialized BitcoinDataCollector with data file: {self.data_file}")
        logger.info(f"Kafka bootstrap servers: {self.kafka_bootstrap_servers}")
        logger.info(f"Kafka topic: {self.kafka_topic}")

    async def stream_1s_ohlc(self):
        uri = "wss://ws-feed.exchange.coinbase.com"
        curr_sec = None
        o = h = l = c = v = None

        while True:
            try:
                async with websockets.connect(uri, ping_interval=20) as ws:
                    # Subscribe to the BTC-USD ticker channel
                    subscribe_msg = {
                        "type": "subscribe",
                        "channels": [{"name": "ticker", "product_ids": ["BTC-USD"]}]
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    logger.info("Connected to Coinbase WebSocket")

                    async for message in ws:
                        msg = json.loads(message)
                        if msg.get("type") != "ticker":
                            continue

                        # Parse timestamp, price, and trade size
                        ts = datetime.fromisoformat(msg["time"].replace("Z", "+00:00"))
                        price = float(msg["price"])
                        size = float(msg.get("last_size", 0.0))
                        sec = int(ts.timestamp())

                        # Initialize or update the current-second bar
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
                            # Prepare data for storage
                            data = {
                                'timestamp': datetime.utcfromtimestamp(curr_sec).isoformat(),
                                'open': o,
                                'high': h,
                                'low': l,
                                'close': c,
                                'volume': v
                            }
                            
                            # Store in CSV
                            with open(self.data_file, 'a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow([data['timestamp'], o, h, l, c, v])
                            
                            # Send to Kafka
                            self.producer.send(self.kafka_topic, value=data)
                            self.producer.flush()
                            
                            logger.info(f"Bar for {data['timestamp']}: O={o}, H={h}, L={l}, C={c}, V={v}")

                            # Start a new bar
                            curr_sec = sec
                            o = h = l = c = price
                            v = size

            except (websockets.ConnectionClosed, asyncio.TimeoutError) as e:
                logger.warning(f"WebSocket disconnected: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}. Restarting in 5s...")
                await asyncio.sleep(5)

    def run(self):
        logger.info("Starting continuous Bitcoin price collection...")
        asyncio.run(self.stream_1s_ohlc())

if __name__ == "__main__":
    logger.info("Starting Bitcoin Data Collector...")
    collector = BitcoinDataCollector()
    collector.run() 