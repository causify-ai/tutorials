"""
Connect to Binance WebSocket and stream BTC/USDT trades in real time.

1. Binance US WebSocket API reference: https://docs.binance.us/#all-market-24h-change-stream
2. websockets library documentation: https://websockets.readthedocs.io/
3. Followed Causify AI coding style guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
4. Linter used: flake8

This module supports real-time ingestion of trade data, which can be integrated
into the Falcon API via callback functions (e.g., to ingest data into /ingest).

To stop the websocket, 'Ctrl+C' in the terminal.
"""
# Packages Import.
import asyncio
import logging
import json
import websockets
import sys
import signal
from typing import Callable, Dict, Any, Coroutine
import logging
import aiohttp
from datetime import datetime

# #############################################################################
# Configure logging
# #############################################################################
# Configure logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_LOG = logging.getLogger(__name__)

# #############################################################################
# Websocket Client
"""
 Connects to Binance WebSocket trade stream and streams data.

 This class handles connecting to the Binance WebSocket and forwarding each
 message to a user-defined async callback. This can be used to send data to
 a Falcon API endpoint or analysis in ipynb notebook.

 Params:
 Class defaults are Bitcoin and Raw Trade Data. Others can be:
 - symbol = ethusdt, bnbbtc
 - stream_type = trace, ticker, depth

 Return:
 Default is raw trade data 
 "e": "trade", = event type
 "E": 1745711352917, = event time in milliseconds
 "s": "BTCUSDT", = symbol
 "t": 30427712, = trade ID
 "p": "94633.70000000", = price
 "q": "0.00247000", = quantity
 "b": 1474818093, = buyer order ID
 "a": 1474818079, = seller order ID
 "T": 1745711352917, = trade time in millisecons
 "m": false, = is the buyer a market maker?
 "M": true = ignore
 """


# log message generator
def generate_log_messages():
    logs = [
        "[WebSocketClient] Connected to Binance/Coinbase stream",
        "[WebSocketClient] Received trade message",
        "[WebSocketClient] Enqueued trade message to asyncio.Queue",
        "[persistent_ws_sender] Pulled message from queue",
        "[persistent_ws_sender] Sent batch to Falcon /ingest endpoint",
        "[Falcon API] Received POST at /ingest endpoint",
        "[Falcon API] Queued trade message via Celery",
        "[Celery Task] Started processing trade",
        "[Celery Task] Finished processing trade",
    ]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [f"{timestamp} - INFO - {msg}" for msg in logs]

generate_log_messages()



# #############################################################################
class WebSocketClient:
    def __init__(self, url: str, platform: str):
 
        self.ws_url = url
        self.platform = platform.lower()
        self.websocket = None
        self.running = False
        self.loop = None
        # Callback handlers
        self.on_message_callback = None
        self.on_error_callback = None
        self.on_close_callback = None
        self.on_open_callback = None
    async def start(self):
        """
        Start the WebSocket connection asynchronously.
        """
        if self.running:
            _LOG.info("WebSocket connection is already running.")
            return
        self.running = True
        self.loop = asyncio.get_running_loop()
        # Set up signal handlers for graceful shutdown.
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        try:
            _LOG.info(f"Connecting to {self.platform} WebSocket Stream: {self.ws_url}")
            async with websockets.connect(self.ws_url) as websocket:
                self.websocket = websocket
                await self._default_on_open()
                # Call on_open callback if defined.
                if self.on_open_callback:
                    await self.on_open_callback()
                else:
                    _LOG.info("Connection opened")
                # Process messages while running.
                MAX_MESSAGES = 1000
                current_message_count = 0
                while self.running and current_message_count < MAX_MESSAGES:
                    # Instead of fake messages, process real data until max reached
                    #if current_message_count >= MAX_MESSAGES:
                     #   _LOG.info("reached max, closing")
                      #  await self.stop()
                       # break
                    message = await websocket.recv()
                    data = json.loads(message)
                    if self.on_message_callback:
                        await self.on_message_callback(data)
                        current_message_count += 1
                    #_LOG.info(f"[WebSocketClient] Received trade message: {message}")
                    #await self._handle_message(message)
                    #current_message_count += 1
                        #message = await websocket.recv()
                        #message = json.dumps({"type": "trade",
                        #"platform": "binance",
                        #"price": "103951.82",
                        #"quantity": "0.00019",
                        #"trade_id": 30464944,
                        #"symbol": "BTCUSDT",
                        #"timestamp": 1747381120129})
                        #await self._handle_message(json.dumps(message))  # If simulating websocket.recv()
                        #await self._handle_message(message)
                    #except websockets.exceptions.ConnectionClosed as e:
                       # await self._handle_close(e.code, e.reason)
                        #break
                    #except Exception as e:
                        #await self._handle_error(e)
                    _LOG.info(f"[WebSocketClient] processed {current_message_count}/{MAX_MESSAGES} messages")
        except Exception as e:
            await self._handle_error(e)
        finally:
            self.running = False
            _LOG.info("WebSocket connection is closed.")
    async def stop(self):
        """
        Stop the WebSocket connection gracefully.
        """
        if not self.running:
            _LOG.warning("WebSocket connection is not running.")
            return
        _LOG.info("Stopping WebSocket connection...")
        self.running = False
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
    async def _handle_message(self, message: str):
        """
        Internal handler for incoming messages.
        """
        try:
            data = json.loads(message)
            # Use custom callback if provided.
            if self.on_message_callback:
                await self.on_message_callback(data)
            else:
                # Default behavior: pretty print the JSON data.
                print(json.dumps(data, indent=2))
                sys.stdout.flush()
        except Exception as e:
            await self._handle_error(e)
    async def _handle_error(self, error: Exception):
        """
        Internal handler for errors.
        """
        if self.on_error_callback:
            await self.on_error_callback(error)
        else:
            _LOG.error(f"Error: {error}")
    async def _handle_close(self, code: int, reason: str):
        """
        Internal handler for connection close.
        """
        if self.on_close_callback:
            await self.on_close_callback(code, reason)
        else:
            _LOG.warning(f"Connection closed: {code} - {reason}")
    async def _default_on_open(self):
        """"
        Handle subscriptions needed for coinbase.
        """
        if self.platform == "coinbase":
            subscribe_message ={
                "type": "subscribe",
                "channels" : ["ticker"],
                "product_ids": ["BTC-USD"]
            }
            await self.websocket.send(json.dumps(subscribe_message))
            print(f"Subscription message sent to {self.ws_url}")
        elif self.platform == "binance":
            print("Binance connection open")
        else:
            print("No default behavior for crypto API platform")
    def set_on_message(self, callback: Callable[[Dict[str, Any]], Coroutine]):
        """
        Set callback for message events.
        Args:
            callback: Async function that accepts a JSON dictionary.
        """
        self.on_message_callback = callback
    def set_on_error(self, callback: Callable[[Exception], Coroutine]):
        """
        Set callback for error events.
        Args:
            callback: Async function that accepts an exception.
        """
        self.on_error_callback = callback
    def set_on_close(self, callback: Callable[[int, str], Coroutine]):
        """
        Set callback for close events.
        Args:
            callback: Async function that accepts code and reason parameters.
        """
        self.on_close_callback = callback
    def set_on_open(self, callback: Callable[[], Coroutine]):
        """
        Set callback for connection open event.
        Args:
            callback: Async function with no parameters.
        """
        self.on_open_callback = callback

    @classmethod
    def from_binance(cls):
            return cls(url="wss://stream.binance.us:9443/ws/btcusdt@trade", platform="BinanceUS")

    @classmethod
    def from_coinbase(cls):
            return cls(url="wss://ws-feed.exchange.coinbase.com", platform="Coinbase")


