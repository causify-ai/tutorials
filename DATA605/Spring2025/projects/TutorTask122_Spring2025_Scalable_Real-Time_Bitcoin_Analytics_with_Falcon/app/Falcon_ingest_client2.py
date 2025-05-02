"""
Stream real-time trade data from Binance and Coinbase and forward it to Falcon WebSocket endpoints.

1. Source data is streamed from:
   - Binance US WebSocket API: https://docs.binance.us/#all-market-24h-change-stream
   - Coinbase Pro WebSocket API: https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
2. Make sure to run the linter (e.g., `flake8`) before committing changes.
   - This enforces compliance with the team's coding style and readability standards.
3. Falcon server documentation: see `Falcon.API.md` for implementation details on the `/ingest` endpoints.

The name of this script should follow the format:
 - `Falcon.IngestClient.py` to reflect that this is the Falcon-facing ingestion client.

Follow the Causify coding style guide for all formatting, naming, and structural conventions:
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""
# Package Imports.
import asyncio
import websockets
import json

# Import class from WebSocketClient script.
from Falcon_WebsocketClient import WebSocketClient  
# ------------------------------------------------------------------------------
# 1. Factory function to create a callback that sends data to the Falcon ingest endpoint
# ------------------------------------------------------------------------------

def build_ingest_callback(uri: str):
    """
    Returns callback function that sends messages to Falcon endpoint.

    Args: uri = Websocket URI of the Flacon API endpoint
    Returns: async function takes dictionary and sends it to Falcon endpoint.
    """
    async def send_to_falcon_ingest(message: dict):
        try:
            # Initiate handshake request to Falcon server to websocket.
            async with websockets.connect(uri) as ws:
                # Send messages converted to JSON string.
                await ws.send(json.dumps(message))
                response = await ws.recv()
                # Recieve response from server.
                print(f"[{uri}] Response from Falcon:", response)
        except Exception as e:
            print(f"[{uri}] Failed to send to Falcon ingest: {e}")
    # Return the customized callback function.
    return send_to_falcon_ingest
# ------------------------------------------------------------------------------
# 2. Generalized runner that starts a WebSocketClient for a given platform and endpoint
# ------------------------------------------------------------------------------
"""
Runs WebsocketClient for the platform specified and sends its messages to the Falcon endpoint.
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

    callback = build_ingest_callback(falcon_uri)
    client.set_on_message(callback)
    # Start the websocket connection and stream data.
    await client.start()

# ------------------------------------------------------------------------------
# 3. Run multiple streaming clients concurrently (Binance and Coinbase)
# ------------------------------------------------------------------------------
"""
Runs Binance and Coinbase clients concurrently by applying .gather()
""" 
async def main():
    await asyncio.gather(
        run_client("binance", "ws://localhost:8000/ingest/binance"),
        run_client("coinbase", "ws://localhost:8000/ingest/coinbase"),
    )

# ------------------------------------------------------------------------------
# 4. Python entry point: runs the main() coroutine when script is executed
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())