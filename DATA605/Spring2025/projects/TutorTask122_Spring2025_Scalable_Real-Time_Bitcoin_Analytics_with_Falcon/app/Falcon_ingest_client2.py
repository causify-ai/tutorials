"""
Stream real-time trade data from Binance and Coinbase and forward it to Falcon WebSocket endpoints.

1. Source data is streamed from:
   - Binance US WebSocket API: https://docs.binance.us/#all-market-24h-change-stream
   - Coinbase Pro WebSocket API: https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
2. Make sure to run the linter `flake8` before committing changes.
3. Falcon server documentation: see `Falcon.API.md` for implementation details on the `/ingest` endpoints.

Follow the Causify coding style guide for all formatting, naming, and structural conventions:
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md


Execution Steps:
Step 0. persistent_ws_sender()
- Persistent sender keeps websocket connection open to Falcon.
- Pulls messages from asyncio.Queue and sends them to Falcon.
- sends a batch of messages every batch_size or batch_interval.
Step 1. build_ingest_callback()
- build ingest callback puts incoming trade messages into the queue.
- Used at the websockclient's on_message handler.
Step 2. run_client()
- Instantiates websocketclient, sets callback, and runs both client and persistent sender.
Step 3. main()
- Starts both stream clients in parallel
Step 4. __main__ block
- launches full asyncio event loop when script is run directly.

"""
# Package Imports.
import asyncio
import websockets
import json
import time
import aiohttp
from aiohttp import ClientSession
import os

API_URL = os.getenv("API_URL", "http://falcon_api:8888")

# Import class from WebSocketClient script.
from Falcon_WebsocketClient import WebSocketClient


# ------------------------------------------------------------------------------
# 0. Persistent http sender function 
# ------------------------------------------------------------------------------

async def persistent_http_sender(api_url: str,
                                 message_queue: asyncio.Queue,
                                 platform: str, 
                                 batch_size: int = 1,
                                 batch_interval: float = 2.0):
    buffer = []
    print(f"[sender] Starting HTTP sender for {platform} → {api_url}")
    last_send = time.time()
    async with aiohttp.ClientSession() as session:
        while True:
            print(f"[sender-debug] queue size before get: {message_queue.qsize()}")
            try:
                msg = await asyncio.wait_for(message_queue.get(), timeout=batch_interval)
                if msg is None:
                    break
                print(f"[sender-debug] dequeued message: {msg}")
                buffer.append(msg)
            except asyncio.TimeoutError:
                pass

            now = time.time()
            if buffer and (len(buffer) >= batch_size or now - last_send >= batch_interval):
                url = f"{api_url}/ingest/{platform}"
                payload = {"trades": buffer}
                print(f"[sender] POST→ {url} payload size={len(buffer)}")
                try:
                    async with session.post(url, json=payload) as resp:
                        text = await resp.text()
                        print(f"[sender] ← {resp.status}: {text}")
                except Exception as e:
                    print(f"[sender] POST error: {e}")
                buffer = []
                last_send = now


# ------------------------------------------------------------------------------
# 1. Factory function to create a callback that sends data to the Falcon ingest endpoint
# ------------------------------------------------------------------------------

def build_ingest_callback(uri: str, message_queue: asyncio.Queue):
    """
    Returns callback function that sends messages to Falcon endpoint. Persistence update
    via the 0. function above, puts messages into a queue. 

    Args: uri = Websocket URI of the Flacon API endpoint
    Returns: async function takes dictionary and sends it to Falcon endpoint.
    """
    async def enqueue_message(message: dict):
        await message_queue.put(message)
    return enqueue_message

# ------------------------------------------------------------------------------
# 2. Generalized runner that starts a WebSocketClient for a given platform and endpoint
# ------------------------------------------------------------------------------
"""
Runs WebsocketClient for the platform specified and sends its messages to the Falcon endpoint.
Modified to work with persistent sender and pass the queue. 
Args: 
    platform (str) binanace or coinbase
    falcon_uri (str) URI of the Falcon API Websocket endpoint
"""
async def run_client(platform: str, falcon_uri: str):
    # Instantiate the client depending on the platform(s).
    if platform.lower() == "binance":
        client = WebSocketClient.from_binance()
    elif platform.lower() == "coinbase":
        client = WebSocketClient.from_coinbase()
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    message_queue = asyncio.Queue()
    callback = build_ingest_callback(falcon_uri, message_queue)
    client.set_on_message(callback)

    # Shut down after client stops
    async def shutdown_watcher():
        await client.start()
        await message_queue.put(None) # Shutdown signal.


    # Start the websocket connection and stream data.
    #await client.start()
    # Run both the client and sender concurrently.
    await asyncio.gather(
        client.start(),
        persistent_http_sender(API_URL,
                              message_queue,
                              platform,
                              batch_size=10,
                              batch_interval=2.0)
    )

# ------------------------------------------------------------------------------
# 3. Run multiple streaming clients concurrently (Binance and Coinbase)
# ------------------------------------------------------------------------------
"""
Runs Binance and Coinbase clients concurrently by applying .gather()
""" 
async def main():
    await asyncio.gather(
        run_client("binance", "ws://falcon_api:8888/ingest/binance"),
        run_client("coinbase", "ws://falcon_api:8888/ingest/coinbase"),
    )

# ------------------------------------------------------------------------------
# 4. Python entry point: runs the main() coroutine when script is executed
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())


