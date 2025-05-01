"""
coinbase_stream.py

Script to connect to Coinbase WebSocket API and stream live Bitcoin trades.
Each trade is automatically passed to the process_trade() pipeline.

- Fetches real-time BTC-USD trades.
- Sends each trade to process_trade().
- Integrates cleanly with btc_trade_API.py.

Run this script to start live ingestion.

Reference:
- Coinbase WebSocket API documentation: https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
"""

import websocket
import json
import logging
from datetime import datetime
from btc_trade_API import process_trade

# -----------------------------------------------------------------------------
# Setup logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# WebSocket Message Handler
# -----------------------------------------------------------------------------

def on_message(ws, message):
    """
    Handle incoming WebSocket messages.
    """
    try:
        data = json.loads(message)
        if data.get('type') == 'match':
            trade_price = float(data['price'])
            trade_time = data['time']

            trade_data = {
                "price": trade_price,
                "time": trade_time
            }

            logger.info(f"Received Trade: {trade_data}")
            process_trade(trade_data)

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def on_error(ws, error):
    """
    Handle WebSocket errors.
    """
    logger.error(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    """
    Handle WebSocket close.
    """
    logger.info("WebSocket connection closed.")

def on_open(ws):
    """
    Send subscription message upon connection.
    """
    subscribe_message = {
        "type": "subscribe",
        "channels": [{"name": "matches", "product_ids": ["BTC-USD"]}]
    }
    ws.send(json.dumps(subscribe_message))
    logger.info("Subscribed to BTC-USD matches.")

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------

def start_coinbase_stream():
    """
    Start the WebSocket client to stream live Bitcoin trades.
    """
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        "wss://ws-feed.exchange.coinbase.com",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    logger.info("Connecting to Coinbase WebSocket...")
    ws.run_forever()

# -----------------------------------------------------------------------------
# Script Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    start_coinbase_stream()
