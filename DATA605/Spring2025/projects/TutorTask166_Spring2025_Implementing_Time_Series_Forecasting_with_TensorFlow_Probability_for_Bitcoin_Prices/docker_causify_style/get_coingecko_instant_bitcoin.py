#!/usr/bin/env python3
"""
realtime_coinbase_ws.py

Continuously streams BTC-USD trades from Coinbase Exchange WebSocket and
aggregates them into 1-second OHLC bars. Appends each bar to a single CSV,
reconnecting automatically on disconnects.
"""
import os
import asyncio
import json
import csv
import logging
from datetime import datetime
import websockets
import yaml
# Configuration
with open("/app/configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
OUTPUT_CSV = config['data']['raw_data']['instant_data']['file']
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

async def stream_1s_ohlc():
    # Use the non-deprecated Coinbase Exchange WebSocket endpoint
    uri = "wss://ws-feed.exchange.coinbase.com"

    # Determine whether we need to write the header
    file_existed = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_existed:
            writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
            logger.info(f"Created new CSV and wrote header: {OUTPUT_CSV}")
            
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

                async for message in ws:
                    msg = json.loads(message)
                    if msg.get("type") != "ticker":
                        continue

                    # Parse timestamp, price, and trade size
                    ts = datetime.fromisoformat(msg["time"].replace("Z", "+00:00"))
                    price = float(msg["price"])
                    size  = float(msg.get("last_size", 0.0))

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
                        # Flush the completed second to CSV
                        row_ts = datetime.utcfromtimestamp(curr_sec).isoformat()
                        with open(OUTPUT_CSV, "a", newline="") as f:
                            csv.writer(f).writerow([row_ts, o, h, l, c, v])
                        logger.info(f"Flushed bar for {row_ts}: O={o}, H={h}, L={l}, C={c}, V={v}")

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

if __name__ == "__main__":
    asyncio.run(stream_1s_ohlc())