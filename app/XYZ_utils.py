import httpx
import time
import sqlite3
import pandas as pd

DB_FILE = "prices.db"

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    response = httpx.get(url, params=params)
    return response.json()["bitcoin"]["usd"]

def store_price(price):
    ts = time.time()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS bitcoin_prices (timestamp REAL, price REAL)")
        conn.execute("INSERT INTO bitcoin_prices VALUES (?, ?)", (ts, price))
        conn.commit()

def get_last_prices(n=10):
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT * FROM bitcoin_prices ORDER BY timestamp DESC LIMIT ?", conn, params=(n,))
        return df.sort_values("timestamp")
