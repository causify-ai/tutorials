"""
Redis_utils.py

This file contains utility functions for connecting to Redis and fetching Bitcoin price data.
It provides a layer of abstraction over the Redis API and CoinGecko API.
It can also be run directly as a command-line tool for data collection and analysis.
"""

import redis
import requests
import json
import time
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Union, Optional, Tuple, Any
import os
import sys
import argparse
import threading
from dotenv import load_dotenv
import threading
import time
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get Redis connection parameters from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Redis Connection
# -----------------------------------------------------------------------------

def connect_to_redis(host: str = None, port: int = None, password: str = None) -> redis.Redis:
    """
    Connect to Redis server.
    
    Args:
        host (str, optional): Redis host address. If None, uses REDIS_HOST from env.
        port (int, optional): Redis port. If None, uses REDIS_PORT from env.
        password (str, optional): Redis password. If None, uses REDIS_PASSWORD from env.
        
    Returns:
        redis.Redis: Redis connection object
        
    Raises:
        redis.ConnectionError: If connection fails
    """
    # Use provided parameters or fall back to environment variables
    host = host if host else REDIS_HOST
    port = port if port is not None else REDIS_PORT
    password = password if password is not None else REDIS_PASSWORD
    
    try:
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            socket_timeout=5,  # 5 seconds timeout for operations
            socket_connect_timeout=5  # 5 seconds timeout for connection
        )
        
        # Test connection
        r.ping()
        logger.info(f"Successfully connected to Redis at {host}:{port}")
        return r
        
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis at {host}:{port}: {e}")
        raise
    except redis.TimeoutError as e:
        logger.error(f"Connection timeout when connecting to Redis at {host}:{port}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to Redis at {host}:{port}: {e}")
        raise

def verify_redis_connection(redis_conn: redis.Redis = None, host: str = None, 
                          port: int = None, password: str = None) -> bool:
    """
    Verify connection to Redis server.
    
    Args:
        redis_conn (redis.Redis, optional): Existing Redis connection to verify.
            If None, a new connection will be attempted.
        host (str, optional): Redis host address if creating new connection.
        port (int, optional): Redis port if creating new connection.
        password (str, optional): Redis password if creating new connection.
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # If no connection is provided, try to establish one
        if redis_conn is None:
            redis_conn = connect_to_redis(host, port, password)
        
        # Test connection with ping
        response = redis_conn.ping()
        
        # Print connection details
        connection_info = redis_conn.connection_pool.connection_kwargs
        host = connection_info.get('host', 'unknown')
        port = connection_info.get('port', 'unknown')
        
        print(f"✅ Successfully connected to Redis at {host}:{port}")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return False
    except redis.TimeoutError as e:
        print(f"❌ Connection timeout when connecting to Redis: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error when verifying Redis connection: {e}")
        return False

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

def monitor_price_updates(pubsub: redis.client.PubSub, duration: int = 3600) -> None:
    """
    Monitor price updates for a specified duration.
    
    Args:
        pubsub (redis.client.PubSub): Redis PubSub object subscribed to a channel
        duration (int): Duration to monitor updates in seconds (default: 3600)
    """
    logger.info(f"Monitoring price updates for {duration} seconds")
    
    start_time = time.time()
    end_time = start_time + duration
    
    # Track price changes
    last_price = None
    max_price = float('-inf')
    min_price = float('inf')
    
    try:
        while time.time() < end_time:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                # Parse message data
                data = json.loads(message['data'])
                price = data.get('usd')
                timestamp = data.get('timestamp')
                
                if price is not None:
                    # Format timestamp
                    dt = datetime.fromtimestamp(timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Calculate price change
                    if last_price is not None:
                        change = price - last_price
                        change_pct = (change / last_price) * 100 if last_price != 0 else 0
                        change_str = f"{change:.2f} ({change_pct:.2f}%)"
                    else:
                        change_str = "N/A"
                    
                    # Update min/max prices
                    if price > max_price:
                        max_price = price
                    if price < min_price:
                        min_price = price
                    
                    # Log price update
                    logger.info(f"[{time_str}] Bitcoin price: ${price:.2f} | Change: {change_str} | Min: ${min_price:.2f} | Max: ${max_price:.2f}")
                    
                    # Update last price
                    last_price = price
            
            # Sleep to avoid busy waiting
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
    
    logger.info("Monitoring completed")

def store_historical_price(redis_conn: redis.Redis, price_data: Dict[str, Any], currency: str = 'usd') -> bool:
    """
    Store historical Bitcoin price data in Redis.
    
    Args:
        redis_conn (redis.Redis): Redis connection object
        price_data (dict): Bitcoin price data point
        currency (str): Currency of the price data (default: 'usd')
        
    Returns:
        bool: True if storage was successful
    """
    try:
        # Get timestamp
        timestamp = price_data.get('timestamp') or int(time.time())
        
        # Add to time series (using sorted set with timestamp as score)
        redis_conn.zadd(
            f"bitcoin:price:history:{currency}", 
            {str(timestamp): price_data[currency]}
        )
        
        # Also store complete data point in another sorted set
        redis_conn.zadd(
            f"bitcoin:price_history:{currency}", 
            {json.dumps(price_data): timestamp}
        )
        
        # Update last update timestamp for historical data
        redis_conn.set("bitcoin:history:last_updated", timestamp)
        
        return True
    except redis.RedisError as e:
        logger.error(f"Error storing historical Bitcoin price data in Redis: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error storing historical Bitcoin data: {e}")
        return False

# -----------------------------------------------------------------------------
# Price Alerting System
# -----------------------------------------------------------------------------

class BitcoinPriceAlertSystem:
    """
    Real-time Bitcoin price alert system using Redis Pub/Sub.
    Monitors price updates and triggers alerts based on thresholds.
    """
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn
        self.pubsub = None
        self.alerts = []
        self.last_price = None
        self.running = False
        self.alert_thread = None
        
    def add_threshold_alert(self, threshold, is_upper=True, message=None):
        """Add a price threshold alert."""
        alert = {
            'type': 'threshold',
            'value': threshold,
            'is_upper': is_upper,
            'triggered': False,
            'message': message or f"{'Upper' if is_upper else 'Lower'} threshold of ${threshold:,.2f} {'exceeded' if is_upper else 'breached'}"
        }
        self.alerts.append(alert)
        logger.info(f"Added {'upper' if is_upper else 'lower'} threshold alert at ${threshold:,.2f}")
        return alert
        
    def add_percent_change_alert(self, percent, period_minutes=5, message=None):
        """Add a percent change alert."""
        alert = {
            'type': 'percent_change',
            'value': percent,
            'period_minutes': period_minutes,
            'triggered': False,
            'historical_prices': [],
            'message': message or f"Price changed by {percent:.1f}% within {period_minutes} minutes"
        }
        self.alerts.append(alert)
        logger.info(f"Added {percent:.1f}% change alert over {period_minutes} minute period")
        return alert
        
    def start_monitoring(self):
        """Start monitoring Bitcoin price updates."""
        if self.running:
            logger.info("Alert system is already running")
            return False
            
        self.running = True
        self.pubsub = create_subscriber(self.redis_conn, channel='bitcoin_price_updates')
        
        # Start the monitoring thread
        self.alert_thread = threading.Thread(target=self._monitor_loop)
        self.alert_thread.daemon = True
        self.alert_thread.start()
        
        logger.info("Bitcoin price alert system started")
        return True
        
    def stop_monitoring(self):
        """Stop monitoring Bitcoin price updates."""
        if not self.running:
            logger.info("Alert system is not running")
            return False
            
        self.running = False
        if self.pubsub:
            self.pubsub.unsubscribe()
        
        if self.alert_thread:
            self.alert_thread.join(timeout=1.0)
            
        logger.info("Bitcoin price alert system stopped")
        return True
        
    def _check_alerts(self, price, timestamp):
        """Check all alerts against the current price."""
        triggered_alerts = []
        
        for alert in self.alerts:
            if alert['type'] == 'threshold':
                if (alert['is_upper'] and price > alert['value']) or \
                   (not alert['is_upper'] and price < alert['value']):
                    if not alert['triggered']:
                        triggered_alerts.append(alert)
                        alert['triggered'] = True
                else:
                    # Reset the trigger if price goes back beyond threshold
                    alert['triggered'] = False
                    
            elif alert['type'] == 'percent_change':
                # Record the current price with timestamp
                alert['historical_prices'].append((timestamp, price))
                
                # Remove prices older than the period
                cutoff_time = timestamp - (alert['period_minutes'] * 60)
                alert['historical_prices'] = [(ts, p) for ts, p in alert['historical_prices'] 
                                           if ts >= cutoff_time]
                
                # Check if we have enough data
                if len(alert['historical_prices']) >= 2:
                    oldest_price = min(alert['historical_prices'], key=lambda x: x[0])[1]
                    percent_change = abs((price - oldest_price) / oldest_price * 100)
                    
                    if percent_change >= alert['value'] and not alert['triggered']:
                        triggered_alerts.append(alert)
                        alert['triggered'] = True
                        # Add actual change to the message
                        direction = "up" if price > oldest_price else "down"
                        alert['current_message'] = f"{alert['message']} (moved {direction} {percent_change:.1f}%)"
                    elif percent_change < alert['value']:
                        alert['triggered'] = False
        
        return triggered_alerts
        
    def _monitor_loop(self):
        """Main monitoring loop that processes incoming price updates."""
        logger.info("Alert monitoring loop started...")
        
        while self.running:
            message = self.pubsub.get_message()
            
            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    price = data.get('usd', 0)
                    timestamp = data.get('last_updated_at', int(time.time()))
                    dt = datetime.fromtimestamp(timestamp)
                    
                    # Check alerts
                    triggered_alerts = self._check_alerts(price, timestamp)
                    
                    # Log any triggered alerts
                    for alert in triggered_alerts:
                        alert_msg = alert.get('current_message', alert['message'])
                        logger.info(f"ALERT at {dt}: {alert_msg}")
                    
                    # Update last price
                    self.last_price = price
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
            
            # Sleep a bit to not consume too much CPU
            time.sleep(0.1)

# Function to run a price simulation for demonstration
def run_price_alert_simulation(redis_conn, base_price, duration_seconds=30, alert_thresholds=None):
    """
    Run a simulation of price fluctuations to demonstrate the alert system.
    
    Parameters:
        redis_conn: Redis connection
        base_price: Starting price to base fluctuations on
        duration_seconds: How long to run the simulation
        alert_thresholds: Dictionary with alert settings (optional)
    
    Returns:
        List of triggered alerts
    """
    import numpy as np
    
    # Create alert system
    alert_system = BitcoinPriceAlertSystem(redis_conn)
    
    # Set up alerts
    if not alert_thresholds:
        # Default alerts
        upper_threshold = base_price * 1.005  # 0.5% above current
        lower_threshold = base_price * 0.995  # 0.5% below current
        
        alert_system.add_threshold_alert(upper_threshold)
        alert_system.add_threshold_alert(lower_threshold, is_upper=False)
        alert_system.add_percent_change_alert(0.2, period_minutes=2)
    else:
        # Custom alerts
        if 'upper' in alert_thresholds:
            alert_system.add_threshold_alert(alert_thresholds['upper'])
        if 'lower' in alert_thresholds:
            alert_system.add_threshold_alert(alert_thresholds['lower'], is_upper=False)
        if 'percent' in alert_thresholds:
            percent = alert_thresholds['percent']
            period = alert_thresholds.get('period_minutes', 2)
            alert_system.add_percent_change_alert(percent, period_minutes=period)
    
    # Start the alert system
    alert_system.start_monitoring()
    logger.info(f"Starting price simulation for {duration_seconds} seconds")
    
    # Start time for our simulation
    start_time = time.time()
    triggered_alerts = []
    
    try:
        while time.time() - start_time < duration_seconds:
            # Create price fluctuation with variance to trigger alerts
            random_change = (np.random.random() - 0.5) * 0.02  # ±1% change
            test_price = base_price * (1 + random_change)
            
            # Create a test data point
            test_data = {
                'usd': test_price,
                'usd_24h_change': random_change * 100,
                'usd_market_cap': 1.9e12,  # Approximate market cap
                'last_updated_at': int(time.time())
            }
            
            # Publish the update
            receivers = publish_price_update(redis_conn, test_data)
            dt = datetime.now().strftime("%H:%M:%S")
            logger.info(f"Published price update: ${test_price:,.2f} (change: {random_change*100:+.2f}%)")
            
            # Sleep for a random time between updates
            time.sleep(np.random.uniform(1.0, 3.0))
        
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    finally:
        # Stop the alert system
        alert_system.stop_monitoring()
        logger.info("Alert system simulation completed")
    
    return alert_system.alerts

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

# -----------------------------------------------------------------------------
# Data Analysis Functions
# -----------------------------------------------------------------------------

def analyze_price_data(df: pd.DataFrame) -> pd.Series:
    """
    Analyze price data and print statistics.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        
    Returns:
        pd.Series: Series indicating anomalies
    """
    # Basic statistics
    logger.info("Basic Statistics:")
    logger.info(f"Mean price: {df['price'].mean():.2f}")
    logger.info(f"Median price: {df['price'].median():.2f}")
    logger.info(f"Min price: {df['price'].min():.2f}")
    logger.info(f"Max price: {df['price'].max():.2f}")
    logger.info(f"Price range: {df['price'].max() - df['price'].min():.2f}")
    logger.info(f"Standard deviation: {df['price'].std():.2f}")
    
    # Calculate percent changes
    if len(df) >= 2:
        hour_change = calculate_percent_change(df, periods=60)  # Assuming 1 minute intervals
        logger.info(f"1-hour change: {hour_change.iloc[-1]:.2f}%")
    
    # Detect anomalies
    anomalies = detect_price_anomalies(df)
    anomaly_count = anomalies.sum()
    logger.info(f"Detected {anomaly_count} price anomalies")
    
    return anomalies

def plot_price_data(df: pd.DataFrame, output_file: str) -> plt.Figure:
    """
    Plot price data and save to file.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        output_file (str): Path to save the output chart
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    timestamps, prices, ma_10, ma_30 = prepare_price_plot_data(df)
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot price data
    ax.plot(df.index, df['price'], label='Price', color='blue')
    
    # Plot moving averages
    ax.plot(df.index, ma_10, label='10-point MA', color='red')
    ax.plot(df.index, ma_30, label='30-point MA', color='green')
    
    # Plot anomalies
    anomalies = detect_price_anomalies(df)
    if anomalies.sum() > 0:
        anomaly_points = df[anomalies]
        ax.scatter(anomaly_points.index, anomaly_points['price'], 
                   color='red', marker='o', s=50, label='Anomalies')
    
    # Set labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Price (USD)')
    ax.set_title('Bitcoin Price Analysis')
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save figure
    plt.tight_layout()
    plt.savefig(output_file)
    logger.info(f"Price chart saved to {output_file}")
    
    return fig

# -----------------------------------------------------------------------------
# Command-line interface
# -----------------------------------------------------------------------------

def parse_collection_arguments(args=None):
    """Parse command line arguments for data collection"""
    parser = argparse.ArgumentParser(description='Collect Bitcoin price data and store in Redis')
    parser.add_argument('--interval', type=int, default=60,
                        help='Time interval between data collections in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=3600,
                        help='Total duration to collect data in seconds (default: 3600)')
    parser.add_argument('--currency', type=str, default='usd',
                        help='Currency to fetch prices in (default: usd)')
    
    return parser.parse_args(args)

def parse_analysis_arguments(args=None):
    """Parse command line arguments for data analysis"""
    parser = argparse.ArgumentParser(description='Analyze Bitcoin price data from Redis')
    parser.add_argument('--hours', type=int, default=24,
                        help='Hours of historical data to analyze (default: 24)')
    parser.add_argument('--currency', type=str, default='usd',
                        help='Currency of price data (default: usd)')
    parser.add_argument('--output', type=str, default='bitcoin_analysis.png',
                        help='Output file for price chart (default: bitcoin_analysis.png)')
    
    return parser.parse_args(args)

def parse_monitor_arguments(args=None):
    """Parse command line arguments for price monitoring"""
    parser = argparse.ArgumentParser(description='Monitor Bitcoin price updates using Redis Pub/Sub')
    parser.add_argument('--channel', type=str, default='bitcoin_price_updates',
                        help='Redis channel to subscribe to (default: bitcoin_price_updates)')
    parser.add_argument('--duration', type=int, default=3600,
                        help='Duration to monitor updates in seconds (default: 3600)')
    
    return parser.parse_args(args)

def parse_verify_arguments(args=None):
    """Parse command line arguments for connection verification"""
    parser = argparse.ArgumentParser(description='Verify Redis connection')
    parser.add_argument('--host', type=str, default=None,
                        help='Redis host address (default: from .env file)')
    parser.add_argument('--port', type=int, default=None,
                        help='Redis port (default: from .env file)')
    parser.add_argument('--password', type=str, default=None,
                        help='Redis password (default: from .env file)')
    
    return parser.parse_args(args)

def run_collection(args=None):
    """Run Bitcoin data collection function"""
    if args is None:
        args = parse_collection_arguments()
    
    logger.info(f"Starting Bitcoin price data collection")
    logger.info(f"Interval: {args.interval} seconds")
    logger.info(f"Duration: {args.duration} seconds ({args.duration/60:.1f} minutes)")
    logger.info(f"Currency: {args.currency}")
    
    try:
        # Connect to Redis using credentials from environment variables
        r = connect_to_redis()
        
        # Collect data
        collect_bitcoin_data(
            redis_conn=r,
            interval=args.interval,
            duration=args.duration,
            currency=args.currency
        )
        
        logger.info("Data collection completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Data collection interrupted by user")
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
        return 1
    
    return 0

def run_analysis(args=None):
    """Run Bitcoin data analysis function"""
    if args is None:
        args = parse_analysis_arguments()
    
    try:
        # Connect to Redis using credentials from environment variables
        r = connect_to_redis()
        
        # Calculate time range
        end_time = int(time.time())
        start_time = end_time - (args.hours * 3600)
        
        logger.info(f"Analyzing Bitcoin price data for the last {args.hours} hours")
        logger.info(f"Time range: {datetime.fromtimestamp(start_time)} to {datetime.fromtimestamp(end_time)}")
        
        # Get price history
        price_history = get_price_history(r, start_time, end_time, args.currency)
        
        if not price_history or len(price_history) == 0:
            logger.error("No data found for the specified time range")
            return 1
        
        logger.info(f"Retrieved {len(price_history)} data points")
        
        # Convert to DataFrame
        df = get_price_dataframe(price_history, args.currency)
        
        # Analyze data
        analyze_price_data(df)
        
        # Plot data
        plot_price_data(df, args.output)
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return 1
    
    return 0

def run_monitor(args=None):
    """Run Bitcoin price monitoring function"""
    if args is None:
        args = parse_monitor_arguments()
    
    try:
        # Connect to Redis using credentials from environment variables
        r = connect_to_redis()
        
        # Create subscriber
        pubsub = create_subscriber(r, args.channel)
        
        # Monitor price updates
        monitor_price_updates(pubsub, args.duration)
        
        # Unsubscribe
        pubsub.unsubscribe()
        
    except Exception as e:
        logger.error(f"Error during monitoring: {e}")
        return 1
    
    return 0

def run_verify(args=None):
    """Verify Redis connection"""
    if args is None:
        args = parse_verify_arguments()
    
    print("Verifying Redis connection...")
    print(f"Using connection parameters:")
    
    # Display connection parameters (using fallbacks from environment if not specified)
    host = args.host if args.host else REDIS_HOST
    port = args.port if args.port is not None else REDIS_PORT
    password_display = "Provided" if args.password or REDIS_PASSWORD else "None"
    
    print(f"- Host: {host}")
    print(f"- Port: {port}")
    print(f"- Password: {password_display}")
    
    # Attempt to verify connection
    success = verify_redis_connection(
        host=args.host,
        port=args.port,
        password=args.password
    )
    
    # Return exit code based on connection success
    return 0 if success else 1

def main():
    """Main entry point for the command-line utility"""
    if len(sys.argv) < 2:
        print("Usage: python Redis_utils.py [collect|analyze|monitor|verify] [options]")
        print("Run 'python Redis_utils.py collect --help', 'python Redis_utils.py analyze --help',")
        print("'python Redis_utils.py monitor --help', or 'python Redis_utils.py verify --help' for more information")
        return 1
    
    command = sys.argv[1]
    
    if command == "collect":
        # Remove the command from sys.argv to allow argparse to work
        sys.argv.pop(1)
        return run_collection()
        
    elif command == "analyze":
        # Remove the command from sys.argv to allow argparse to work
        sys.argv.pop(1)
        return run_analysis()
        
    elif command == "monitor":
        # Remove the command from sys.argv to allow argparse to work
        sys.argv.pop(1)
        return run_monitor()
        
    elif command == "verify":
        # Remove the command from sys.argv to allow argparse to work
        sys.argv.pop(1)
        return run_verify()
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: collect, analyze, monitor, verify")
        return 1

if __name__ == "__main__":
    exit(main())


