import asyncio
#from Falcon_utils import BinanceWebSocketClient
from Falcon_utils import BinanceWebSocketClient

# Example usage:
async def main():
    # Create client instance
    client = BinanceWebSocketClient("btcusdt")
    
    # Define custom callbacks
    async def on_message(data):
        print(f"Price: {data.get('p', 'N/A')}, Quantity: {data.get('q', 'N/A')}")
    
    async def on_open():
        print("Connection established to Binance.US")
    
    async def on_error(error):
        print(f"Error occurred: {error}")
    
    async def on_close(code, reason):
        print(f"Connection closed with code {code}: {reason}")
    '''
    # Set callbacks
    client.set_on_message(on_message)
    client.set_on_open(on_open)
    client.set_on_error(on_error)
    client.set_on_close(on_close)
    '''
    
    # Start the client
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())