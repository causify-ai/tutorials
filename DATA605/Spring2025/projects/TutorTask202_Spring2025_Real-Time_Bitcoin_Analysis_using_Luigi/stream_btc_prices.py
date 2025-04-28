"""
Real-time Bitcoin price logger using Coinbase WebSocket API.

- Streams BTC-USD price data and logs it to a CSV file.
- Automatically handles reconnections and maintains a local data log.

Reference:
- Coinbase WebSocket API:
  https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
"""
import asyncio
import websockets
import json
import csv
import os
from datetime import datetime


class CoinbaseWebSocketCSVLogger:
    """
    Logs BTC-USD ticker updates to a local CSV using WebSocket streaming.
    """

    def __init__(self, product_id='BTC-USD', output_file='btc_price_log.csv'):
        self.url = "wss://ws-feed.exchange.coinbase.com"
        self.product_id = product_id
        self.output_path = os.path.join("data", output_file)
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.output_path):
            with open(self.output_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "price"])

    async def connect(self):
        """
        Maintain WebSocket connection and route messages.
        """  
        while True:
            try:
                async with websockets.connect(self.url) as websocket:
                    await self.subscribe(websocket)
                    await self.listen(websocket)
            except Exception as e:
                print(f"Connection error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)

    async def subscribe(self, websocket):
        """
        Subscribe to the BTC-USD ticker channel.
        """

        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": [self.product_id]}]
        }
        await websocket.send(json.dumps(subscribe_message))

    async def listen(self, websocket):
        """
        Listen to incoming messages and log them.
        """

        print("Streaming BTC prices to CSV...")
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'ticker':
                self.log_to_csv(data)

    def log_to_csv(self, data):
        """
        Write a ticker message to CSV if valid.

        :param data: JSON dictionary containing timestamp and price
        """

        ts = data.get("time", "")
        price = data.get("price", "")
        if ts and price:
            timestamp = datetime.utcnow().isoformat()
            print(f"{timestamp} | Price: ${price}")
            with open(self.output_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, price])


if __name__ == "__main__":
    client = CoinbaseWebSocketCSVLogger()
    asyncio.run(client.connect())
