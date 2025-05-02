#!/usr/bin/env python3
"""
Script to monitor Bitcoin price updates using Redis Pub/Sub.
"""

import argparse
import logging
import time
import json
import threading
from datetime import datetime

from Redis_utils import (
    connect_to_redis,
    create_subscriber
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Redis connection parameters
REDIS_HOST = 'redis-14816.c98.us-east-1-4.ec2.redns.redis-cloud.com'
REDIS_PORT = 14816
REDIS_PASSWORD = 'TilZb88poJQOWMmfeXXajEKzkrbyBxCG'

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Monitor Bitcoin price updates using Redis Pub/Sub')
    parser.add_argument('--channel', type=str, default='bitcoin_price_updates',
                        help='Redis channel to subscribe to (default: bitcoin_price_updates)')
    parser.add_argument('--duration', type=int, default=3600,
                        help='Duration to monitor updates in seconds (default: 3600)')
    
    return parser.parse_args()

def monitor_price_updates(pubsub, duration=3600):
    """Monitor price updates for a specified duration"""
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

def main():
    """Main function"""
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Connect to Redis
        r = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
        
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

if __name__ == "__main__":
    exit(main()) 