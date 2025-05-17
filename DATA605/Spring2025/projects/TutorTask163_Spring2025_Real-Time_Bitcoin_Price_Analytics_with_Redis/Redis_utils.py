"""
Redis_utils.py

This file contains utility functions for connecting to Redis and fetching Bitcoin price data.
It provides a layer of abstraction over the Redis API and CoinGecko API.
"""

import redis
import requests
import json
import time
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Optional, Tuple, Any

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Redis Connection
# -----------------------------------------------------------------------------

def connect_to_redis(host: str, port: int, password: str) -> redis.Redis:
    """
    Connect to Redis server.
    
    Args:
        host (str): Redis host address
        port (int): Redis port
        password (str): Redis password
        
    Returns:
        redis.Redis: Redis connection object
    """
    try:
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
        # Test connection
        r.ping()
        logger.info("Successfully connected to Redis")
        return r
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

# -----------------------------------------------------------------------------
# Bitcoin Data Fetching from CoinGecko API
# -----------------------------------------------------------------------------

def fetch_bitcoin_price(currency: str = 'usd') -> Dict[str, Any]:
    """
    Fetch current Bitcoin price from CoinGecko API.
    
    Args:
        currency (str): Currency to fetch price in (default: 'usd')
        
    Returns:
        dict: Bitcoin price data
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        # Add timestamp for when we fetched the data
        data['bitcoin']['timestamp'] = int(time.time())
        
        logger.info(f"Successfully fetched Bitcoin price: {data['bitcoin'][currency]} {currency.upper()}")
        return data['bitcoin']
    except requests.RequestException as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        raise

def fetch_bitcoin_historical(days: int = 1, currency: str = 'usd') -> Dict[str, List]:
    """
    Fetch historical Bitcoin price data from CoinGecko API.
    
    Args:
        days (int): Number of days of data to fetch (default: 1)
        currency (str): Currency to fetch prices in (default: 'usd')
        
    Returns:
        dict: Historical Bitcoin price data
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={currency}&days={days}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched historical Bitcoin data for the last {days} days")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching historical Bitcoin data: {e}")
        raise

# -----------------------------------------------------------------------------
# Redis Data Storage
# -----------------------------------------------------------------------------

def store_bitcoin_price(redis_conn: redis.Redis, price_data: Dict[str, Any], currency: str = 'usd') -> bool:
    """
    Store Bitcoin price data in Redis.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        price_data (dict): Bitcoin price data from CoinGecko API
        currency (str): Currency of the price data (default: 'usd')
        
    Returns:
        bool: True if storage was successful
    """
    try:
        # Store current price as a string
        redis_conn.set(f"bitcoin:current_price:{currency}", price_data[currency])
        
        # Store timestamp of last update
        redis_conn.set("bitcoin:last_updated", price_data['timestamp'])
        
        # Store all data as a hash
        redis_conn.hset(f"bitcoin:data:{currency}", mapping={
            'price': price_data[currency],
            'market_cap': price_data[f"{currency}_market_cap"],
            'volume_24h': price_data[f"{currency}_24h_vol"],
            'change_24h': price_data[f"{currency}_24h_change"],
            'last_updated_at': price_data['last_updated_at'],
            'timestamp': price_data['timestamp']
        })
        
        # Add to time series (using sorted set with timestamp as score)
        redis_conn.zadd(
            f"bitcoin:price_history:{currency}", 
            {json.dumps(price_data): price_data['timestamp']}
        )
        
        logger.info(f"Successfully stored Bitcoin price data in Redis")
        return True
    except redis.RedisError as e:
        logger.error(f"Error storing Bitcoin price data in Redis: {e}")
        return False

def get_current_bitcoin_price(redis_conn: redis.Redis, currency: str = 'usd') -> float:
    """
    Get current Bitcoin price from Redis.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        currency (str): Currency of the price data (default: 'usd')
        
    Returns:
        float: Current Bitcoin price
    """
    try:
        price = redis_conn.get(f"bitcoin:current_price:{currency}")
        if price:
            return float(price)
        else:
            logger.warning("No current Bitcoin price found in Redis")
            return None
    except redis.RedisError as e:
        logger.error(f"Error retrieving Bitcoin price from Redis: {e}")
        raise

def get_bitcoin_data(redis_conn: redis.Redis, currency: str = 'usd') -> Dict[str, Any]:
    """
    Get all Bitcoin data from Redis.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        currency (str): Currency of the price data (default: 'usd')
        
    Returns:
        dict: Bitcoin data including price, market cap, etc.
    """
    try:
        data = redis_conn.hgetall(f"bitcoin:data:{currency}")
        if data:
            # Convert numeric values from strings
            for key in ['price', 'market_cap', 'volume_24h', 'change_24h', 'last_updated_at', 'timestamp']:
                if key in data:
                    data[key] = float(data[key])
            return data
        else:
            logger.warning("No Bitcoin data found in Redis")
            return None
    except redis.RedisError as e:
        logger.error(f"Error retrieving Bitcoin data from Redis: {e}")
        raise

def get_price_history(redis_conn: redis.Redis, start_time: int = None, end_time: int = None, 
                     currency: str = 'usd') -> List[Dict[str, Any]]:
    """
    Get Bitcoin price history from Redis within a specific time range.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        start_time (int): Start time as Unix timestamp (default: None for no lower bound)
        end_time (int): End time as Unix timestamp (default: None for no upper bound)
        currency (str): Currency of the price data (default: 'usd')
        
    Returns:
        list: List of Bitcoin price data points
    """
    try:
        # Set default time range if not provided
        if start_time is None:
            start_time = '-inf'
        if end_time is None:
            end_time = '+inf'
            
        # Get data from sorted set within time range
        result = redis_conn.zrangebyscore(
            f"bitcoin:price_history:{currency}", 
            start_time, 
            end_time, 
            withscores=True
        )
        
        # Parse JSON data
        history = []
        for item, score in result:
            data = json.loads(item)
            history.append(data)
            
        logger.info(f"Retrieved {len(history)} Bitcoin price records from history")
        return history
    except redis.RedisError as e:
        logger.error(f"Error retrieving Bitcoin price history from Redis: {e}")
        raise

# -----------------------------------------------------------------------------
# Redis Pub/Sub for Real-time Updates
# -----------------------------------------------------------------------------

def publish_price_update(redis_conn: redis.Redis, price_data: Dict[str, Any], 
                        channel: str = 'bitcoin_price_updates') -> int:
    """
    Publish Bitcoin price update to a Redis channel.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        price_data (dict): Bitcoin price data
        channel (str): Redis channel to publish to (default: 'bitcoin_price_updates')
        
    Returns:
        int: Number of clients that received the message
    """
    try:
        message = json.dumps(price_data)
        receivers = redis_conn.publish(channel, message)
        logger.info(f"Published price update to {receivers} subscribers")
        return receivers
    except redis.RedisError as e:
        logger.error(f"Error publishing price update: {e}")
        raise

def create_subscriber(redis_conn: redis.Redis, channel: str = 'bitcoin_price_updates') -> redis.client.PubSub:
    """
    Create a Redis subscriber for a channel.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        channel (str): Redis channel to subscribe to (default: 'bitcoin_price_updates')
        
    Returns:
        redis.client.PubSub: PubSub object for receiving messages
    """
    try:
        pubsub = redis_conn.pubsub()
        pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel: {channel}")
        return pubsub
    except redis.RedisError as e:
        logger.error(f"Error creating subscriber: {e}")
        raise

# -----------------------------------------------------------------------------
# Time Series Analysis
# -----------------------------------------------------------------------------

def get_price_dataframe(price_history: List[Dict[str, Any]], currency: str = 'usd') -> pd.DataFrame:
    """
    Convert price history list to a Pandas DataFrame.
    
    Args:
        price_history (list): List of Bitcoin price data points
        currency (str): Currency of the price data (default: 'usd')
        
    Returns:
        pd.DataFrame: DataFrame with price data
    """
    # Extract relevant data
    data = []
    for item in price_history:
        data.append({
            'timestamp': item['timestamp'],
            'price': item[currency],
            'market_cap': item.get(f"{currency}_market_cap"),
            'volume_24h': item.get(f"{currency}_24h_vol"),
            'change_24h': item.get(f"{currency}_24h_change")
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Set datetime as index
    df = df.set_index('datetime')
    
    return df

def calculate_moving_average(df: pd.DataFrame, window: int = 10, column: str = 'price') -> pd.Series:
    """
    Calculate moving average of a column in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        window (int): Window size for moving average (default: 10)
        column (str): Column to calculate moving average for (default: 'price')
        
    Returns:
        pd.Series: Moving average series
    """
    return df[column].rolling(window=window).mean()

def calculate_percent_change(df: pd.DataFrame, periods: int = 1, column: str = 'price') -> pd.Series:
    """
    Calculate percent change over a number of periods.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        periods (int): Number of periods to calculate change over (default: 1)
        column (str): Column to calculate percent change for (default: 'price')
        
    Returns:
        pd.Series: Percent change series
    """
    return df[column].pct_change(periods=periods) * 100

def detect_price_anomalies(df: pd.DataFrame, threshold: float = 2.0, column: str = 'price') -> pd.Series:
    """
    Detect anomalies in price data using Z-score method.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        threshold (float): Z-score threshold for anomaly detection (default: 2.0)
        column (str): Column to detect anomalies in (default: 'price')
        
    Returns:
        pd.Series: Boolean series indicating anomalies
    """
    # Calculate Z-scores
    z_scores = (df[column] - df[column].mean()) / df[column].std()
    
    # Identify anomalies
    anomalies = abs(z_scores) > threshold
    
    return anomalies

# -----------------------------------------------------------------------------
# Data Collection Helper Functions
# -----------------------------------------------------------------------------

def collect_bitcoin_data(redis_conn: redis.Redis, interval: int = 60, 
                       duration: int = 3600, currency: str = 'usd') -> None:
    """
    Collect Bitcoin price data at regular intervals and store in Redis.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        interval (int): Time interval between data collections in seconds (default: 60)
        duration (int): Total duration to collect data in seconds (default: 3600)
        currency (str): Currency to fetch prices in (default: 'usd')
    """
    start_time = time.time()
    end_time = start_time + duration
    
    logger.info(f"Starting data collection for {duration/60:.1f} minutes at {interval} second intervals")
    
    while time.time() < end_time:
        try:
            # Fetch Bitcoin price data
            price_data = fetch_bitcoin_price(currency)
            
            # Store in Redis
            store_bitcoin_price(redis_conn, price_data, currency)
            
            # Publish price update
            publish_price_update(redis_conn, price_data)
            
            # Wait for next interval
            time.sleep(interval)
            
        except Exception as e:
            logger.error(f"Error during data collection: {e}")
            time.sleep(interval)  # Continue with next interval
    
    logger.info("Data collection completed")

# -----------------------------------------------------------------------------
# Visualization Helper Functions
# -----------------------------------------------------------------------------

def prepare_price_plot_data(df: pd.DataFrame) -> Tuple[List, List, List, List]:
    """
    Prepare Bitcoin price data for plotting.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        
    Returns:
        tuple: (timestamps, prices, moving_avg_10, moving_avg_30)
    """
    # Calculate moving averages
    df['ma_10'] = calculate_moving_average(df, window=10)
    df['ma_30'] = calculate_moving_average(df, window=30)
    
    # Convert to lists for plotting
    timestamps = df.index.tolist()
    prices = df['price'].tolist()
    ma_10 = df['ma_10'].tolist()
    ma_30 = df['ma_30'].tolist()
    
    return timestamps, prices, ma_10, ma_30


