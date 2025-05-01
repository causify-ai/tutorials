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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sklearn.model_selection import train_test_split
# from pycaret.classification import compare_models


# -----------------------------------------------------------------------------
# Logging  
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------

# database configuration
RDS_HOST = ""
RDS_PORT = 5432
RDS_DATABASE = "bitcoin_db"
RDS_USERNAME = "bitcoin" 
RDS_PASSWORD = ""  

# -----------------------------------------------------------------------------
# Database Connection Functions
# -----------------------------------------------------------------------------

def get_db_connection():
    """
    Create a connection to the Amazon RDS PostgreSQL database.
    
    :return: Database connection object
    """
    logger.info("Connecting to RDS database")
    try:
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DATABASE,
            user=RDS_USERNAME,
            password=RDS_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def create_tables_if_not_exist():
    """
    Create the necessary tables for Bitcoin data if they don't exist.
    """
    logger.info("Creating tables if they don't exist")
    
    # SQL to create raw_bitcoin_prices table
    create_raw_table_sql = """
    CREATE TABLE IF NOT EXISTS raw_bitcoin_prices (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        price_usd NUMERIC(20,8),
        volume_usd NUMERIC(24,2),
        market_cap_usd NUMERIC(24,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_raw_bitcoin_prices_timestamp 
    ON raw_bitcoin_prices(timestamp);
    """
    
    # SQL to create hourly_bitcoin_prices table
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
            conn.close()

# -----------------------------------------------------------------------------
# Bitcoin Data Functions
# -----------------------------------------------------------------------------

def fetch_bitcoin_data_from_coingecko():
    """
    Fetch current Bitcoin price data from CoinGecko API.
    
    :return: Dictionary containing Bitcoin price data
    """
    logger.info("Fetching Bitcoin data from CoinGecko")
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        # Extract relevant data
        bitcoin_data = {
            "timestamp": datetime.utcnow(),
            "price_usd": data["market_data"]["current_price"]["usd"],
            "volume_usd": data["market_data"]["total_volume"]["usd"],
            "market_cap_usd": data["market_data"]["market_cap"]["usd"]
        }
        
        return bitcoin_data
    except Exception as e:
        logger.error(f"Error fetching Bitcoin data: {e}")
        raise

def insert_raw_bitcoin_data(data):
    """
    Insert Bitcoin data into the raw_bitcoin_prices table.
    
    :param data: Dictionary containing Bitcoin price data
    :return: ID of the inserted record
    """
    logger.info("Inserting raw Bitcoin data into database")
    
    insert_sql = """
    INSERT INTO raw_bitcoin_prices (timestamp, price_usd, volume_usd, market_cap_usd)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            insert_sql, 
            (
                data["timestamp"],
                data["price_usd"],
                data["volume_usd"],
                data["market_cap_usd"]
            )
        )
        
        record_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Data inserted successfully with ID: {record_id}")
        return record_id
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()

def fetch_and_store_bitcoin_data():
    """
    Fetch Bitcoin data from API and store it in the database.
    
    :return: ID of the inserted record
    """
    data = fetch_bitcoin_data_from_coingecko()
    record_id = insert_raw_bitcoin_data(data)
    return record_id

# -----------------------------------------------------------------------------
# Time Series Analysis Functions
# -----------------------------------------------------------------------------

def aggregate_hourly_data():
    """
    Aggregate raw Bitcoin data into hourly data points.
    """
    logger.info("Aggregating hourly Bitcoin data")
    
    # Step 1: Get all hours that need aggregation
    hours_query = """
    SELECT DISTINCT date_trunc('hour', timestamp) as hour
    FROM raw_bitcoin_prices
    WHERE date_trunc('hour', timestamp) NOT IN (SELECT timestamp FROM hourly_bitcoin_prices)
    ORDER BY hour;
    """
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all hours that need aggregation
        cur.execute(hours_query)
        hours = [row[0] for row in cur.fetchall()]
        
        if not hours:
            logger.info("No new hours to aggregate")
            return
        
        logger.info(f"Aggregating {len(hours)} hours of data")
        
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
            
            # Insert into hourly_bitcoin_prices
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
            
            cur.execute(insert_query, (hour, open_price, high_price, low_price, close_price, avg_volume))
        
        conn.commit()
        logger.info("Hourly data aggregated successfully")
    except Exception as e:
        logger.error(f"Error aggregating hourly data: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()

def get_bitcoin_price_history(days=7):
    """
    Retrieve Bitcoin price history from the database.
    
    :param days: Number of days of history to retrieve
    :return: DataFrame containing price history
    """
    logger.info(f"Retrieving {days} days of Bitcoin price history")
    
    query = """
    SELECT timestamp, price_usd, volume_usd, market_cap_usd
    FROM raw_bitcoin_prices
    WHERE timestamp > NOW() - INTERVAL '%s DAY'
    ORDER BY timestamp;
    """
    
    conn = None
    try:
        conn = get_db_connection()
        
        # Read data directly into pandas DataFrame
        df = pd.read_sql_query(query, conn, params=(days,))
        
        logger.info(f"Retrieved {len(df)} records of Bitcoin price history")
        return df
    except Exception as e:
        logger.error(f"Error retrieving Bitcoin price history: {e}")
        raise
    finally:
        if conn:
            conn.close()

def fetch_and_store_historical_bitcoin_data(days=30):
    """
    Fetch historical Bitcoin price data from CoinGecko API and store it in the database.
    
    :param days: Number of days of historical data to fetch (max 90 for free tier)
    :return: Number of records inserted
    """
    logger.info(f"Fetching historical Bitcoin data for the past {days} days")
    
    # CoinGecko API endpoint for historical data (daily)
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": str(days),
        "interval": "daily"  # daily data points
    }
    
    records_inserted = 0
    conn = None
    
    try:
        # Fetch historical data
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process prices (comes as [timestamp, price] pairs)
        prices = data["prices"]  
        volumes = data["total_volumes"]  
        market_caps = data["market_caps"]  
        
        # Prepare data for batch insert
        historical_data = []
        for i in range(len(prices)):
            # Convert millisecond timestamp to datetime
            timestamp = datetime.fromtimestamp(prices[i][0] / 1000)
            
            datapoint = {
                "timestamp": timestamp,
                "price_usd": prices[i][1],
                "volume_usd": volumes[i][1],
                "market_cap_usd": market_caps[i][1]
            }
            historical_data.append(datapoint)
        
        # Insert data into database
        for datapoint in historical_data:
            try:
                record_id = insert_raw_bitcoin_data(datapoint)
                records_inserted += 1
            except Exception as e:
                logger.warning(f"Couldn't insert record for {datapoint['timestamp']}: {e}")
                # Continue with other records
                continue
        
        logger.info(f"Successfully inserted {records_inserted} historical records")
        return records_inserted
        
    except Exception as e:
        logger.error(f"Error fetching or storing historical data: {e}")
        raise

# -----------------------------------------------------------------------------
# Data Analysis Functions (Keeping the template examples)
# -----------------------------------------------------------------------------

def split_data(df: pd.DataFrame, target_column: str, test_size: float = 0.2):
    """
    Split the dataset into training and testing sets.

    :param df: full dataset
    :param target_column: name of the target column
    :param test_size: proportion of test data (default = 0.2)

    :return: X_train, X_test, y_train, y_test
    """
    logger.info("Splitting data into train and test sets")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=42)

def calculate_moving_average(df: pd.DataFrame, window: int = 24) -> pd.DataFrame:
    """
    Calculate moving average for Bitcoin prices.
    
    :param df: DataFrame containing Bitcoin price data with timestamp and price_usd columns
    :param window: Window size for moving average in hours
    :return: DataFrame with original data and moving average column
    """
    logger.info(f"Calculating {window}-hour moving average")
    
    # Ensure DataFrame is sorted by timestamp
    df = df.sort_values('timestamp')
    
    # Calculate moving average
    df[f'ma_{window}h'] = df['price_usd'].rolling(window=window).mean()
    
    return df


