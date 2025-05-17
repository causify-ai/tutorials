# bitcoin_utils.py
"""
Utility functions for real-time Bitcoin data ingestion and Snowflake interaction.
"""

import os
import logging
import requests
from datetime import datetime
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def connect_to_snowflake():
    """
    Establish connection to Snowflake using credentials from the .env file.

    :return: Snowflake connection object
    """
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    logger.info("✅ Connected to Snowflake")
    return conn


def create_btc_table(conn):
    """
    Create the BTC_PRICES table if it does not exist.

    :param conn: Snowflake connection object
    :return: None
    """
    create_stmt = """
    CREATE TABLE IF NOT EXISTS BTC_PRICES (
        timestamp TIMESTAMP,
        price_usd FLOAT
    );
    """
    conn.cursor().execute(create_stmt)
    logger.info("✅ Table BTC_PRICES is ready.")


def fetch_bitcoin_price():
    """
    Fetch the current Bitcoin price in USD using the CoinGecko API.

    :return: Latest price as float
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    price = response.json()["bitcoin"]["usd"]
    logger.info(f"💰 Current Bitcoin Price: ${price}")
    return price


def insert_bitcoin_price(conn, price_usd):
    """
    Insert a new Bitcoin price with current timestamp into the Snowflake table.

    :param conn: Snowflake connection object
    :param price_usd: Bitcoin price in USD (float)
    :return: None
    """
    insert_stmt = """
    INSERT INTO BTC_PRICES (timestamp, price_usd)
    VALUES (%s, %s);
    """
    conn.cursor().execute(insert_stmt, (datetime.utcnow(), price_usd))
    logger.info("📥 Inserted Bitcoin price into Snowflake.")


def fetch_btc_data(conn):
    """
    Retrieve all rows from BTC_PRICES table in Snowflake.

    :param conn: Snowflake connection object
    :return: Pandas DataFrame of BTC_PRICES
    """
    query = "SELECT * FROM BTC_PRICES ORDER BY timestamp ASC;"
    df = pd.read_sql(query, conn)
    logger.info("📊 Fetched data from Snowflake.")
    return df
