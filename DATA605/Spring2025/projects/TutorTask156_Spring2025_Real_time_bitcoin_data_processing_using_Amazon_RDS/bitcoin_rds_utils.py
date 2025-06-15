"""
bitcoin_rds_utils.py

This file contains utility functions that support the Bitcoin price data processing
with Amazon RDS.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Functions here handle database connections, data fetching, and time series analysis.
"""

import pandas as pd
import logging
import psycopg2
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from psycopg2 import pool
from sklearn.model_selection import train_test_split

# from pycaret.classification import compare_models
import os
from dotenv import load_dotenv
import time
import functools



# Logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Configuration


# Load environment variables from .env file
load_dotenv()

# Check if required environment variables are set
required_env_vars = ["RDS_HOST", "RDS_DATABASE", "RDS_USER", "RDS_PASSWORD"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.warning(
        "Please create a .env file with these variables or set them in your environment"
    )

# Database configuration
RDS_CONFIG = {
    "host": os.getenv("RDS_HOST"),
    "port": int(os.getenv("RDS_PORT", 5432)),
    "database": os.getenv("RDS_DATABASE"),
    "user": os.getenv("RDS_USER"),
    "password": os.getenv("RDS_PASSWORD"),
}

# API configuration
API_CONFIG = {
    "base_url": "https://api.coingecko.com/api/v3",
    "headers": {
        "Accept": "application/json",
        "User-Agent": "Bitcoin RDS Integration",
        "x-cg-api-key": os.getenv("COINGECKO_API_KEY"),
    },
    "api_key": os.getenv("COINGECKO_API_KEY"),
}

# Create a global connection pool (initialized once)
_connection_pool = None


# Database Connection Functions
# -----------------------------------------------------------------------------


def get_db_connection_pool(min_connections=1, max_connections=10):
    """
    Create or return a connection pool for the Amazon RDS PostgreSQL database.

    :param min_connections: Minimum number of connections to keep open
    :param max_connections: Maximum number of connections allowed
    :return: Connection pool object
    """
    global _connection_pool

    if _connection_pool is None:
        logger.info("Creating database connection pool")
        try:
            _connection_pool = pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                host=RDS_CONFIG["host"],
                port=RDS_CONFIG["port"],
                database=RDS_CONFIG["database"],
                user=RDS_CONFIG["user"],
                password=RDS_CONFIG["password"],
            )
            logger.info(
                f"Connection pool created with {min_connections}-{max_connections} connections"
            )
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    return _connection_pool


def get_db_connection():
    """
    Get a connection from the pool, or create a direct connection if pool not initialized.

    :return: Database connection object
    """
    # Try to get a connection from the pool first
    pool_obj = get_db_connection_pool()
    if pool_obj:
        try:
            conn = pool_obj.getconn()
            logger.debug("Got connection from the pool")
            return conn
        except Exception as e:
            logger.warning(
                f"Error getting connection from pool: {e}, falling back to direct connection"
            )

    # Fall back to direct connection if pool fails
    logger.info("Creating direct database connection")
    try:
        conn = psycopg2.connect(
            host=RDS_CONFIG["host"],
            port=RDS_CONFIG["port"],
            database=RDS_CONFIG["database"],
            user=RDS_CONFIG["user"],
            password=RDS_CONFIG["password"],
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def release_db_connection(conn):
    """
    Release a connection back to the pool if it came from the pool,
    otherwise close the connection.

    :param conn: Database connection to release or close
    """
    global _connection_pool

    if conn is None:
        return

    if _connection_pool is not None:
        try:
            _connection_pool.putconn(conn)
            logger.debug("Released connection back to the pool")
        except Exception as e:
            logger.warning(f"Error returning connection to pool: {e}, closing directly")
            try:
                conn.close()
            except Exception:
                pass
    else:
        try:
            conn.close()
            logger.debug("Closed direct database connection")
        except Exception as e:
            logger.warning(f"Error closing database connection: {e}")


def with_db_connection(func):
    """
    Decorator to automatically handle database connections.
    The wrapped function will receive a connection as its first argument.

    :param func: Function to wrap with database connection handling
    :return: Wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = get_db_connection()
            return func(conn, *args, **kwargs)
        finally:
            if conn is not None:
                release_db_connection(conn)

    return wrapper


def create_tables_if_not_exist():
    """
    Create the necessary tables for Bitcoin data if they don't exist.
    """
    logger.info("Creating tables if they don't exist")

    # SQL to create raw_bitcoin_prices table
    create_raw_table_sql = """
    CREATE TABLE IF NOT EXISTS raw_bitcoin_prices (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL UNIQUE,
        price_usd NUMERIC(20,8),
        volume_usd NUMERIC(24,2),
        market_cap_usd NUMERIC(24,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_raw_bitcoin_prices_timestamp 
    ON raw_bitcoin_prices(timestamp);
    """

    # SQL to create hourly_bitcoin_prices table with improved index
    create_hourly_table_sql = """
    CREATE TABLE IF NOT EXISTS hourly_bitcoin_prices (
        timestamp TIMESTAMP PRIMARY KEY,
        open_price_usd NUMERIC(20,8),
        high_price_usd NUMERIC(20,8),
        low_price_usd NUMERIC(20,8),
        close_price_usd NUMERIC(20,8),
        volume_usd NUMERIC(24,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_hourly_bitcoin_prices_close
    ON hourly_bitcoin_prices(close_price_usd);
    """

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Create tables
        cur.execute(create_raw_table_sql)
        cur.execute(create_hourly_table_sql)

        conn.commit()
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            release_db_connection(conn)


def add_unique_constraint_to_raw_table():
    """Add unique constraint to timestamp column if it doesn't exist"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # First check if constraint exists
        cur.execute(
            """
        SELECT COUNT(*) FROM pg_constraint 
        WHERE conname = 'raw_bitcoin_prices_timestamp_key' 
        AND conrelid = 'raw_bitcoin_prices'::regclass;
        """
        )
        constraint_exists = cur.fetchone()[0] > 0

        if not constraint_exists:
            # Add unique constraint to timestamp column
            alter_sql = "ALTER TABLE raw_bitcoin_prices ADD CONSTRAINT raw_bitcoin_prices_timestamp_key UNIQUE (timestamp);"
            cur.execute(alter_sql)
            conn.commit()
            logger.info("Added unique constraint to timestamp column")
        else:
            logger.info("Unique constraint already exists on timestamp column")

    except Exception as e:
        logger.error(f"Error adding unique constraint: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            release_db_connection(conn)



# Bitcoin Data Functions
# -----------------------------------------------------------------------------


def fetch_bitcoin_data_from_coingecko(retry_count=3, retry_delay=2):
    """
    Fetch current Bitcoin price data from CoinGecko API with retry logic.

    :param retry_count: Number of retry attempts for API calls
    :param retry_delay: Delay between retries in seconds
    :return: Dictionary containing Bitcoin price data
    """
    logger.info("Fetching Bitcoin data from CoinGecko")
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
    }

    # Initialize variables for retry logic
    attempts = 0
    last_exception = None

    while attempts < retry_count:
        try:
            response = requests.get(
                url, params=params, headers=API_CONFIG["headers"], timeout=10
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()

            # Calculate 24h price change percentage
            price_change_24h = data["market_data"]["price_change_percentage_24h"]

            # Extract relevant data
            bitcoin_data = {
                "timestamp": datetime.utcnow(),
                "price_usd": data["market_data"]["current_price"]["usd"],
                "volume_usd": data["market_data"]["total_volume"]["usd"],
                "market_cap_usd": data["market_data"]["market_cap"]["usd"],
                "price_change_24h": price_change_24h,
            }

            return bitcoin_data
        except Exception as e:
            attempts += 1
            last_exception = e
            logger.warning(f"API call attempt {attempts} failed: {e}")

            if attempts < retry_count:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

    # If we get here, all retries failed
    logger.error(f"All API call attempts failed: {last_exception}")
    raise last_exception


@with_db_connection
def insert_raw_bitcoin_data(conn, data):
    """
    Insert Bitcoin data into the raw_bitcoin_prices table.

    :param conn: Database connection (injected by decorator)
    :param data: Dictionary containing Bitcoin price data
    :return: ID of the inserted record
    """
    logger.info("Inserting raw Bitcoin data into database")

    insert_sql = """
    INSERT INTO raw_bitcoin_prices (timestamp, price_usd, volume_usd, market_cap_usd)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """

    try:
        cur = conn.cursor()

        cur.execute(
            insert_sql,
            (
                data["timestamp"],
                data["price_usd"],
                data["volume_usd"],
                data["market_cap_usd"],
            ),
        )

        record_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Data inserted successfully with ID: {record_id}")
        return record_id
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()


def fetch_and_store_bitcoin_data():
    """
    Fetch Bitcoin data from API and store it in the database.

    :return: ID of the inserted record
    """
    data = fetch_bitcoin_data_from_coingecko()
    record_id = insert_raw_bitcoin_data(data)
    return record_id



# Time Series Analysis Functions
# -----------------------------------------------------------------------------


@with_db_connection
def aggregate_hourly_data(conn, days_to_aggregate=7):
    """
    Aggregate raw Bitcoin data into hourly data points for the specified days.

    :param conn: Database connection (injected by decorator)
    :param days_to_aggregate: Number of days to look back for aggregation
    """
    logger.info(
        f"Aggregating hourly Bitcoin data for the last {days_to_aggregate} days"
    )

    # Step 1: Get hours from the specified time period that need aggregation
    hours_query = """
    SELECT DISTINCT date_trunc('hour', timestamp) as hour
    FROM raw_bitcoin_prices
    WHERE timestamp > NOW() - INTERVAL '%s days'
    AND date_trunc('hour', timestamp) NOT IN (SELECT timestamp FROM hourly_bitcoin_prices)
    ORDER BY hour;
    """

    try:
        cur = conn.cursor()

        # Get all hours that need aggregation
        cur.execute(hours_query, (days_to_aggregate,))
        hours = [row[0] for row in cur.fetchall()]

        if not hours:
            logger.info("No new hours to aggregate")
            return

        logger.info(f"Aggregating {len(hours)} hours of data")

        # Prepare batch insert parameters
        batch_data = []
        batch_size = 100  # Process in batches of 100 hours

        # For each hour, calculate OHLC values
        for hour in hours:
            # Query for data in this hour
            hour_data_query = """
            SELECT 
                price_usd, volume_usd
            FROM raw_bitcoin_prices
            WHERE timestamp >= %s AND timestamp < %s + INTERVAL '1 hour'
            ORDER BY timestamp;
            """

            cur.execute(hour_data_query, (hour, hour))
            rows = cur.fetchall()

            if not rows:
                continue

            # Calculate OHLC values
            open_price = rows[0][0]  # First price
            close_price = rows[-1][0]  # Last price
            high_price = max(row[0] for row in rows)
            low_price = min(row[0] for row in rows)
            avg_volume = sum(row[1] for row in rows) / len(rows)

            # Add to batch
            batch_data.append(
                (hour, open_price, high_price, low_price, close_price, avg_volume)
            )

            # If batch is full, insert and reset
            if len(batch_data) >= batch_size:
                execute_batch_insert(cur, batch_data)
                batch_data = []

        # Insert any remaining records
        if batch_data:
            execute_batch_insert(cur, batch_data)

        conn.commit()
        logger.info("Hourly data aggregated successfully")
    except Exception as e:
        logger.error(f"Error aggregating hourly data: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()


def execute_batch_insert(cursor, batch_data):
    """
    Execute batch insert for hourly data.

    :param cursor: Database cursor
    :param batch_data: List of data tuples to insert
    """
    insert_query = """
    INSERT INTO hourly_bitcoin_prices
    (timestamp, open_price_usd, high_price_usd, low_price_usd, close_price_usd, volume_usd)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (timestamp) 
    DO UPDATE SET
        open_price_usd = EXCLUDED.open_price_usd,
        high_price_usd = EXCLUDED.high_price_usd,
        low_price_usd = EXCLUDED.low_price_usd,
        close_price_usd = EXCLUDED.close_price_usd,
        volume_usd = EXCLUDED.volume_usd,
        created_at = CURRENT_TIMESTAMP;
    """

    # Use executemany for batch insert
    cursor.executemany(insert_query, batch_data)


@with_db_connection
def get_bitcoin_price_history(conn, days=7, use_hourly=False):
    """
    Retrieve Bitcoin price history from the database.

    :param conn: Database connection (injected by decorator)
    :param days: Number of days of history to retrieve
    :param use_hourly: Whether to use hourly data (True) or raw data (False)
    :return: DataFrame containing price history
    """
    logger.info(
        f"Retrieving {days} days of Bitcoin price history (hourly={use_hourly})"
    )

    # Different queries depending on whether we want hourly or raw data
    if use_hourly:
        query = """
        SELECT 
            timestamp, 
            open_price_usd,
            high_price_usd,
            low_price_usd, 
            close_price_usd as price_usd,
            volume_usd
        FROM hourly_bitcoin_prices
        WHERE timestamp > NOW() - INTERVAL '%s days'
        ORDER BY timestamp;
        """
    else:
        query = """
        SELECT timestamp, price_usd, volume_usd, market_cap_usd
        FROM raw_bitcoin_prices
        WHERE timestamp > NOW() - INTERVAL '%s days'
        ORDER BY timestamp;
        """

    try:
        # Read data directly into pandas DataFrame
        df = pd.read_sql_query(query, conn, params=(days,))

        logger.info(f"Retrieved {len(df)} records of Bitcoin price history")

        # Ensure proper datetime format
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df
    except Exception as e:
        logger.error(f"Error retrieving Bitcoin price history: {e}")
        raise


def fetch_and_store_historical_bitcoin_data(days=30):
    """
    Fetch historical Bitcoin price data from CoinGecko API and store it in the database.
    Replaces any existing data for the specified period.

    :param days: Number of days of historical data to fetch (max 90 for free tier)
    :return: Number of records inserted
    """
    logger.info(f"Fetching historical Bitcoin data for the past {days} days")

    # First, clear out any existing data in the date range we're about to fetch
    start_date = datetime.now() - timedelta(days=days)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Delete existing data in the date range
        delete_sql = "DELETE FROM raw_bitcoin_prices"  # Deletes all data
        cursor.execute(delete_sql)
        conn.commit()
        logger.info(f"Cleared existing data from the past {days} days")
    except Exception as e:
        logger.error(f"Error clearing existing data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        release_db_connection(conn)

    # Set days to fetch (ensure within limits)
    days_to_fetch = min(days, 90)  # Max 90 days for free tier
    records_inserted = 0

    # CoinGecko API endpoint for historical data - fetch all at once
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days_to_fetch)}

    try:
        # Fetch historical data
        logger.info(f"Making single API call for {days_to_fetch} days of data")
        response = requests.get(
            url, params=params, headers=API_CONFIG["headers"], timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Process prices (comes as [timestamp, price] pairs)
        prices = data["prices"]
        volumes = data["total_volumes"]
        market_caps = data["market_caps"]

        logger.info(f"Received {len(prices)} price data points from API")

        # Prepare data for batch insert
        historical_data = []
        for i in range(len(prices)):
            # Convert millisecond timestamp to datetime
            timestamp = datetime.fromtimestamp(prices[i][0] / 1000)

            datapoint = {
                "timestamp": timestamp,
                "price_usd": prices[i][1],
                "volume_usd": volumes[i][1] if i < len(volumes) else 0,
                "market_cap_usd": market_caps[i][1] if i < len(market_caps) else 0,
            }
            historical_data.append(datapoint)

        # Create database connection
        conn = get_db_connection()

        try:
            cursor = conn.cursor()

            # Simple insert SQL
            insert_sql = """
            INSERT INTO raw_bitcoin_prices (timestamp, price_usd, volume_usd, market_cap_usd)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """

            # Insert data into database
            for datapoint in historical_data:
                cursor.execute(
                    insert_sql,
                    (
                        datapoint["timestamp"],
                        datapoint["price_usd"],
                        datapoint["volume_usd"],
                        datapoint["market_cap_usd"],
                    ),
                )
                result = cursor.fetchone()
                if result is not None:
                    records_inserted += 1

            conn.commit()
            logger.info(f"Successfully inserted {records_inserted} new records")

        except Exception as e:
            logger.error(f"Database error during data insertion: {e}")
            conn.rollback()
        finally:
            cursor.close()
            release_db_connection(conn)

    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")

    logger.info(
        f"Historical data fetch complete. Inserted {records_inserted} new records"
    )
    return records_inserted



# Data Analysis Functions
# -----------------------------------------------------------------------------


def calculate_moving_average(df: pd.DataFrame, window: int = 24) -> pd.DataFrame:
    """
    Calculate moving average for Bitcoin prices.

    :param df: DataFrame containing Bitcoin price data with timestamp and price_usd columns
    :param window: Window size for moving average in hours
    :return: DataFrame with original data and moving average column
    """
    logger.info(f"Calculating {window}-hour moving average")

    # Ensure DataFrame is sorted by timestamp and make a copy to avoid SettingWithCopyWarning
    df = df.sort_values("timestamp").copy()

    # Calculate moving average
    df[f"ma_{window}h"] = df["price_usd"].rolling(window=window).mean()

    return df


def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Calculate the Relative Strength Index (RSI) for Bitcoin prices.

    The RSI is a momentum oscillator that measures the speed and change of price movements.
    Traditionally, RSI values of 70 or above indicate overbought conditions (suggesting a potential
    price correction downwards), while RSI values of 30 or below indicate oversold conditions
    (suggesting a potential price correction upwards).

    :param df: DataFrame containing Bitcoin price data with timestamp and price_usd columns
    :param window: Period for RSI calculation (default=14)
    :return: DataFrame with original data and RSI column
    """
    logger.info(f"Calculating {window}-period RSI")

    # Ensure DataFrame is sorted by timestamp and make a copy to avoid SettingWithCopyWarning
    df = df.sort_values("timestamp").copy()

    # Calculate price changes
    df["price_change"] = df["price_usd"].diff()

    # Create columns for gains and losses
    df["gain"] = np.where(df["price_change"] > 0, df["price_change"], 0)
    df["loss"] = np.where(df["price_change"] < 0, abs(df["price_change"]), 0)

    # Calculate average gains and losses over the specified window
    avg_gain = df["gain"].rolling(window=window).mean()
    avg_loss = df["loss"].rolling(window=window).mean()

    # Calculate the RS (Relative Strength) and RSI
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # Clean up intermediate columns
    df.drop(["price_change", "gain", "loss"], axis=1, inplace=True)

    return df


def calculate_bollinger_bands(
    df: pd.DataFrame, window: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands for Bitcoin prices.

    Bollinger Bands consist of:
    - A middle band (simple moving average)
    - An upper band (middle band + standard deviation)
    - A lower band (middle band - standard deviation)

    :param df: DataFrame containing Bitcoin price data with timestamp and price_usd columns
    :param window: Window size for the moving average
    :param num_std: Number of standard deviations for the upper/lower bands
    :return: DataFrame with original data and Bollinger Bands columns
    """
    logger.info(
        f"Calculating Bollinger Bands with {window}-period window and {num_std} std"
    )

    # Ensure DataFrame is sorted by timestamp and make a copy
    df = df.sort_values("timestamp").copy()

    # Calculate middle band (simple moving average)
    df["bb_middle"] = df["price_usd"].rolling(window=window).mean()

    # Calculate standard deviation
    rolling_std = df["price_usd"].rolling(window=window).std()

    # Calculate upper and lower bands
    df["bb_upper"] = df["bb_middle"] + (rolling_std * num_std)
    df["bb_lower"] = df["bb_middle"] - (rolling_std * num_std)

    return df


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """
    Calculate Moving Average Convergence Divergence (MACD) for Bitcoin prices.

    MACD consists of:
    - MACD line: Difference between fast and slow EMAs
    - Signal line: EMA of the MACD line
    - Histogram: Difference between MACD line and signal line

    :param df: DataFrame containing Bitcoin price data with timestamp and price_usd columns
    :param fast_period: Period for the fast EMA
    :param slow_period: Period for the slow EMA
    :param signal_period: Period for the signal line EMA
    :return: DataFrame with original data and MACD columns
    """
    logger.info(
        f"Calculating MACD with fast={fast_period}, slow={slow_period}, signal={signal_period}"
    )

    # Ensure DataFrame is sorted by timestamp and make a copy
    df = df.sort_values("timestamp").copy()

    # Calculate fast and slow EMAs
    df["ema_fast"] = df["price_usd"].ewm(span=fast_period, adjust=False).mean()
    df["ema_slow"] = df["price_usd"].ewm(span=slow_period, adjust=False).mean()

    # Calculate MACD line
    df["macd"] = df["ema_fast"] - df["ema_slow"]

    # Calculate signal line
    df["macd_signal"] = df["macd"].ewm(span=signal_period, adjust=False).mean()

    # Calculate histogram
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Remove intermediate columns
    df.drop(["ema_fast", "ema_slow"], axis=1, inplace=True)

    return df
