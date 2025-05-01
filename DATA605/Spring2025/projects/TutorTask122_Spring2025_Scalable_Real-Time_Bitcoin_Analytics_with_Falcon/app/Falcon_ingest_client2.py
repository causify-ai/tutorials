"""
The 
"""
import asyncio
import websockets
import json

from Falcon_WebsocketClient import WebSocketClient  # Adjust if your module path is different

async def send_message_to_falcon(uri, message):
    """
    Connect to Falcon API WebSocket endpoint and send the message.
    """
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Response from Falcon ({uri}):", response)

async def stream_binance_data():
    """
    Stream Binance data and forward to Falcon ingest endpoint.
    """
    binance_client = WebSocketClient.from_binance()

    async def on_binance_message(data):
        print("Forwarding Binance trade to Falcon...")
        await send_message_to_falcon("ws://localhost:8000/ingest/binance", data)

    binance_client.set_on_message(on_binance_message)
    await binance_client.start()

async def stream_coinbase_data():
    """
    Stream Coinbase data and forward to Falcon ingest endpoint.
    """
    coinbase_client = WebSocketClient.from_coinbase()

    async def on_coinbase_message(data):
        print("Forwarding Coinbase trade to Falcon...")
        await send_message_to_falcon("ws://localhost:8000/ingest/coinbase", data)

    coinbase_client.set_on_message(on_coinbase_message)
    await coinbase_client.start()

async def main():
    # Run Binance and Coinbase streamers at the same time
    await asyncio.gather(
        stream_binance_data(),
        stream_coinbase_data(),
    )

if __name__ == "__main__":
    asyncio.run(main())
