#  File: bitcoin_utils.py

import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["bitcoin"]["usd"]

def save_to_db(price, db_host="localhost"):
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "bitcoin_db")
    
    engine = 
create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
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
    return df

def save_to_csv(df, csv_path="output/bitcoin_price_log.csv"):
    if not os.path.exists(os.path.dirname(csv_path)):
        os.makedirs(os.path.dirname(csv_path))
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, mode='a', header=False, index=False)
    return csv_path

