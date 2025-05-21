import os
import time
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# === Configuration ===
DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "bitcoin_db")


MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

# === Step 1: Fetch Bitcoin Price ===
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()["bitcoin"]["usd"]

# === Step 2: Connect to TimescaleDB ===
def connect_to_db_with_retry():
    connection_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            engine = create_engine(connection_url)
            # Try a test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f" Connected to DB on attempt {attempt}")
            return engine
        except OperationalError as e:
            print(f"⏳ Waiting for DB... attempt {attempt}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    print(" Could not connect to the database after retries.")
    exit(1)

# === Step 3: Save Price to DB and CSV ===
def save_data(price, engine):
    timestamp = datetime.utcnow()
    df = pd.DataFrame([{"timestamp": timestamp, "price": price}])

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bitcoin_prices (
                timestamp TIMESTAMPTZ,
                price DOUBLE PRECISION
            );
        """))
        df.to_sql("bitcoin_prices", conn, if_exists="append", index=False)
        print(f"[{timestamp}]  Saved Bitcoin price: ${price}")

    # Also save to CSV
    csv_path = "bitcoin_price_log.csv"
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, mode='w', index=False)
    else:
        df.to_csv(csv_path, mode='a', header=False, index=False)

# === Main Execution ===
if __name__ == "__main__":
    try:
        price = fetch_bitcoin_price()
        engine = connect_to_db_with_retry()
        save_data(price, engine)
    except Exception as e:
        print(f" Error occurred: {e}")
