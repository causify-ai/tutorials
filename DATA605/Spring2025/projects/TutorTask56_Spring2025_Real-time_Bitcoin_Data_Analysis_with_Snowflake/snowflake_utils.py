import os
import pandas as pd
import snowflake.connector
import requests
from datetime import datetime
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

load_dotenv()

def connect_to_snowflake():
    """Establishes a connection to Snowflake using key pair authentication."""
    private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY", "rsa_key.pem")
    with open(private_key_path, "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    private_key_bytes = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        private_key=private_key_bytes
    )

def fetch_bitcoin_price():
    """Fetches the current Bitcoin price from the CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    price = response.json()["bitcoin"]["usd"]
    timestamp = datetime.utcnow().isoformat()
    return {"timestamp": timestamp, "price": price}

def insert_price_to_snowflake(conn, data):
    """Inserts a single row of Bitcoin price data into the Snowflake table."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitcoin_prices (
            timestamp TIMESTAMP,
            price FLOAT
        )
    """)
    cursor.execute("""
        INSERT INTO bitcoin_prices (timestamp, price)
        VALUES (%s, %s)
    """, (data["timestamp"], data["price"]))
    conn.commit()
    cursor.close()

def query_all_prices():
    """Queries all Bitcoin price data from Snowflake and returns it as a DataFrame."""
    conn = connect_to_snowflake()
    query = "SELECT * FROM bitcoin_prices ORDER BY timestamp"
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

def load_historical_prices_to_snowflake():
    """Fetches 90-day historical BTC prices from CoinGecko and inserts them into Snowflake."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "90",
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    conn = connect_to_snowflake()
    cursor = conn.cursor()

    table = os.getenv("SNOWFLAKE_TABLE", "bitcoin_prices")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            timestamp TIMESTAMP,
            price FLOAT
        )
    """)

    inserted = 0
    for _, row in df.iterrows():
        ts = row["timestamp"].to_pydatetime()
        cursor.execute(f"""
            INSERT INTO {table} (timestamp, price)
            VALUES (%s, %s)
        """, (ts, row["price"]))
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {inserted} historical rows into {table}.")
