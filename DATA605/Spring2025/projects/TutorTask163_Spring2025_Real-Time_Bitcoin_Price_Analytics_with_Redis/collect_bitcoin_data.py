#!/usr/bin/env python3
"""
Script to collect Bitcoin price data at regular intervals and store in Redis.
"""

import argparse
import logging
import time
from Redis_utils import (
    connect_to_redis,
    collect_bitcoin_data
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
    parser = argparse.ArgumentParser(description='Collect Bitcoin price data and store in Redis')
    parser.add_argument('--interval', type=int, default=60,
                        help='Time interval between data collections in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=3600,
                        help='Total duration to collect data in seconds (default: 3600)')
    parser.add_argument('--currency', type=str, default='usd',
                        help='Currency to fetch prices in (default: usd)')
    
    return parser.parse_args()

def main():
    """Main function"""
    # Parse arguments
    args = parse_arguments()
    
    logger.info(f"Starting Bitcoin price data collection")
    logger.info(f"Interval: {args.interval} seconds")
    logger.info(f"Duration: {args.duration} seconds ({args.duration/60:.1f} minutes)")
    logger.info(f"Currency: {args.currency}")
    
    try:
        # Connect to Redis
        r = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
        
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

if __name__ == "__main__":
    exit(main()) 