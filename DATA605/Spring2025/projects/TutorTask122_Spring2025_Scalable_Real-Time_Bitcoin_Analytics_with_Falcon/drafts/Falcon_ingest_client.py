import asyncio
import websockets


async def send_message():
    uri = "ws://localhost:8000/reports"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Name of the log: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(response)

async def stream_data():
    while True:
        choice = input("Type 'binance' or 'coinbase': ").strip().lower()
        if choice != "binance" and choice != "coinbase":
            print("Invalid choice. Please type 'binance' or 'coinbase'.")
            return
        uri = f"ws://localhost:8000/ingest/{choice}"
        async with websockets.connect(uri) as websocket:
            message = input("Enter fake data: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(response)

if __name__ == "__main__":
    asyncio.run(stream_data())