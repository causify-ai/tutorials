#!/usr/bin/env python3
"""
Script to analyze Bitcoin price data stored in Redis.
"""

import argparse
import logging
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

from Redis_utils import (
    connect_to_redis,
    get_price_history,
    get_price_dataframe,
    calculate_moving_average,
    calculate_percent_change,
    detect_price_anomalies,
    prepare_price_plot_data
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
    parser = argparse.ArgumentParser(description='Analyze Bitcoin price data from Redis')
    parser.add_argument('--hours', type=int, default=24,
                        help='Hours of historical data to analyze (default: 24)')
    parser.add_argument('--currency', type=str, default='usd',
                        help='Currency of price data (default: usd)')
    parser.add_argument('--output', type=str, default='bitcoin_analysis.png',
                        help='Output file for price chart (default: bitcoin_analysis.png)')
    
    return parser.parse_args()

def analyze_price_data(df):
    """Analyze price data and print statistics"""
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

def plot_price_data(df, output_file):
    """Plot price data and save to file"""
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

def main():
    """Main function"""
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Connect to Redis
        r = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
        
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

if __name__ == "__main__":
    exit(main()) 