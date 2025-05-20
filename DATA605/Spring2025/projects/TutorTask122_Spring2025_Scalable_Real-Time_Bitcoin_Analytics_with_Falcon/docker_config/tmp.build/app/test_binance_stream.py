import asyncio
#from Falcon_utils import BinanceWebSocketClient
from Falcon_utils import BinanceWebSocketClient

async def print_trade(trade: dict) -> None:
    """
    Print the full raw trade message for exploration.
    """
    print("\nNEW TRADE:")
    for key, value in trade.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    print("Starting Binance WebSocket client...")  # confirm script starts
    client = BinanceWebSocketClient()
    try:
        asyncio.run(client.listen(print_trade))
    except Exception as e:
        print(f"ERROR: {e}")
