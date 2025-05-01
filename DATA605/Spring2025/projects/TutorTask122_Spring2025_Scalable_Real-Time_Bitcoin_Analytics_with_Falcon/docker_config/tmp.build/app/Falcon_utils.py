"""
Connect to Binance WebSocket and stream BTC/USDT trades in real time.

1. Binance WebSocket API reference: https://binance-docs.github.io/apidocs/spot/en/#trade-streams
2. websockets library documentation: https://websockets.readthedocs.io/
3. Followed Causify AI coding style guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
4. Linter used: flake8

This module supports real-time ingestion of trade data, which can be integrated
into the Falcon API via callback functions (e.g., to ingest data into /ingest).
"""

import asyncio
import logging
import json
from typing import Callable, Awaitable

import websockets

_LOG = logging.getLogger(__name__)


class BinanceWebSocketClient:
    """
    Connects to Binance WebSocket trade stream and streams data.

    This class handles connecting to the Binance WebSocket and forwarding each
    message to a user-defined async callback. This can be used to send data to
    a Falcon API endpoint or for local analysis.
    """

    def __init__(self, symbol: str = "btcusdt"):
        """
        Initialize the WebSocket client for the given trading pair.

        :param symbol: Trading pair to subscribe to (default: btcusdt)
        """
        self.symbol = symbol.lower()
        self.url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"

    async def listen(self, callback: Callable[[dict], Awaitable[None]]) -> None:
        """
        Connect to the WebSocket and stream data to the given callback.

        :param callback: An async function that will receive each trade message.
        :return: None
        """
        _LOG.info("Connecting to Binance WebSocket for symbol: %s", self.symbol)
        async with websockets.connect(self.url) as ws:
            while True:
                msg = await ws.recv()
                trade = json.loads(msg)
                _LOG.debug("Received trade: %s", trade)
                await callback(trade)
