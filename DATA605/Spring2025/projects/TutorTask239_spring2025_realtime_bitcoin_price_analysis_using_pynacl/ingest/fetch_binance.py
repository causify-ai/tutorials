import websocket, json
import pandas as pd
import threading
from datetime import datetime
from crypto.encrypt import encrypt_data, sender_private, recipient_public
from storage.db_handler import write_price, init_db
from queue import Queue
import time

# Initialize database
init_db()

candles_queue = Queue()
ws_url = "wss://stream.binance.us:9443/ws/btcusdt@trade"

# Variables to accumulate trades
candlestick_data = []

def on_message(ws, message):
    global candlestick_data

    data = json.loads(message)
    price = float(data['p'])
    trade_time = pd.to_datetime(data['T'], unit='ms') 

    candlestick_data.append((trade_time, price))
    # print(f"New Trade at {trade_time}: {price}")

def process_candles():
    global candlestick_data

    while True:
        if not candlestick_data:
            continue

        df = pd.DataFrame(candlestick_data, columns=['timestamp', 'price'])
        df.set_index('timestamp', inplace=True)
        completed_minutes = df.index.floor('min').unique()

        for minute in completed_minutes:
            df_minute = df[(df.index >= minute) & (df.index < minute + pd.Timedelta(minutes=1))]
            if df_minute.empty:
                continue

            o = df_minute['price'].iloc[0]
            h = df_minute['price'].max()
            l = df_minute['price'].min()
            c = df_minute['price'].iloc[-1]

            candles_queue.put((minute, o, h, l, c))  # ✅ Send to queue

            encrypted_close = encrypt_data(str(c), sender_private, recipient_public)
            write_price(encrypted_close)

            print(f"Encrypted and Saved Candlestick: {minute} - O:{o} H:{h} L:{l} C:{c}")

        # Remove old trades
        last_processed_minute = max(completed_minutes)
        candlestick_data = [(ts, price) for ts, price in candlestick_data if ts >= last_processed_minute + pd.Timedelta(minutes=1)]

        time.sleep(10)

def start_stream():
    ws = websocket.WebSocketApp(ws_url, on_message=on_message)
    threading.Thread(target=process_candles, daemon=True).start()
    ws.run_forever()

if __name__ == '__main__':
    print("📈 Starting data collection...")
    start_stream()
