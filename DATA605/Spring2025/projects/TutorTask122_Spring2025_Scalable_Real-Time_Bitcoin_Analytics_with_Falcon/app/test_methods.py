import asyncio
import json
import logging
import sys
import websockets
import signal
from typing import Any, Callable, Coroutine, Dict
from websocketclient import WebSocketClient
# Your WebSocketClient class is assumed to be already defined above here.

# Example 1: Connect to Binance

async def binance_example():
    client = WebSocketClient.from_binance()

    async def on_message(data):
        print("Binance message received:")
        print(json.dumps(data, indent=2))
        # Stop after receiving the first message for demo purposes
        await client.stop()

    client.set_on_message(on_message)

    await client.start()

# Example 2: Connect to Coinbase

async def coinbase_example():
    client = WebSocketClient.from_coinbase()

    async def on_open():
        # Coinbase requires a subscription message right after connecting
        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": ["BTC-USD"]}]
        }
        await client.websocket.send(json.dumps(subscribe_message))
        print("Sent subscription message to Coinbase.")

    async def on_message(data):
        print("Coinbase message received:")
        print(json.dumps(data, indent=2))
        # Stop after receiving the first message for demo purposes
        # await client.stop()

    client.set_on_open(on_open)
    client.set_on_message(on_message)

    await client.start()

# Main

if __name__ == "__main__":
    # Pick one to run
    choice = input("Type 'binance' or 'coinbase': ").strip().lower()

    if choice == "binance":
        asyncio.run(binance_example())
    elif choice == "coinbase":
        asyncio.run(coinbase_example())
    else:
        print("Invalid choice. Please type 'binance' or 'coinbase'.")