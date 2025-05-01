#!/usr/bin/env python3
"""
Test script for Redis_utils.py
"""

import time
import logging
from Redis_utils import (
    connect_to_redis,
    fetch_bitcoin_price,
    store_bitcoin_price,
    get_current_bitcoin_price,
    get_bitcoin_data,
    publish_price_update
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Redis connection parameters
REDIS_HOST = 'redis-14816.c98.us-east-1-4.ec2.redns.redis-cloud.com'
REDIS_PORT = 14816
REDIS_PASSWORD = 'TilZb88poJQOWMmfeXXajEKzkrbyBxCG'

def test_redis_connection():
    """Test Redis connection"""
    logger.info("Testing Redis connection...")
    try:
        r = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
        logger.info("Redis connection successful!")
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

def test_bitcoin_data_fetch():
    """Test Bitcoin data fetching"""
    logger.info("Testing Bitcoin data fetch...")
    try:
        data = fetch_bitcoin_price()
        logger.info(f"Bitcoin price data: {data}")
        return data
    except Exception as e:
        logger.error(f"Bitcoin data fetch failed: {e}")
        return None

def test_store_and_retrieve():
    """Test storing and retrieving data from Redis"""
    logger.info("Testing store and retrieve functionality...")
    
    # Connect to Redis
    r = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
    
    # Fetch Bitcoin data
    price_data = fetch_bitcoin_price()
    
    # Store in Redis
    store_bitcoin_price(r, price_data)
    
    # Retrieve from Redis
    price = get_current_bitcoin_price(r)
    data = get_bitcoin_data(r)
    
    logger.info(f"Retrieved price: {price}")
    logger.info(f"Retrieved data: {data}")
    
    return price, data

def test_pubsub():
    """Test Redis Pub/Sub functionality"""
    logger.info("Testing Redis Pub/Sub...")
    
    # Connect to Redis
    r = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
    
    # Fetch Bitcoin data
    price_data = fetch_bitcoin_price()
    
    # Publish update
    receivers = publish_price_update(r, price_data)
    
    logger.info(f"Published to {receivers} receivers")
    
    return receivers

if __name__ == "__main__":
    logger.info("Starting Redis utils tests...")
    
    # Test Redis connection
    r = test_redis_connection()
    if r is None:
        logger.error("Redis connection test failed. Exiting...")
        exit(1)
    
    # Test Bitcoin data fetch
    price_data = test_bitcoin_data_fetch()
    if price_data is None:
        logger.error("Bitcoin data fetch test failed. Exiting...")
        exit(1)
    
    # Test store and retrieve
    price, data = test_store_and_retrieve()
    
    # Test Pub/Sub
    receivers = test_pubsub()
    
    logger.info("All tests completed!") 