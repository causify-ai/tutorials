import os
import time
import json
import requests
import pandas as pd
import schedule
from datetime import datetime
import matplotlib.pyplot as plt
from db_manager import DatabaseManager
from utils import setup_logging

# Setup logging
logger = setup_logging()

# Configuration
FETCH_INTERVAL = int(os.environ.get('FETCH_INTERVAL', 60))  # seconds
CHARTS_DIR = os.environ.get('CHARTS_DIR', '/data/charts')
API_URL = os.environ.get('API_URL', 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true')

# Ensure charts directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'bitcoin_data')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')

# Initialize database manager
db_manager = DatabaseManager(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def fetch_bitcoin_data():
    """Fetch Bitcoin data from CoinGecko API"""
    try:
        logger.info("Fetching Bitcoin data...")
        response = requests.get(API_URL)
        response.raise_for_status()
        
        data = response.json()
        timestamp = datetime.now()
        
        bitcoin_data = data.get('bitcoin', {})
        if not bitcoin_data:
            logger.error("No Bitcoin data found in the response")
            return None
        
        # Add timestamp to the data
        bitcoin_data['timestamp'] = timestamp
        
        logger.info(f"Data fetched successfully: {bitcoin_data}")
        return bitcoin_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

def process_and_store_data(data):
    """Process and store Bitcoin data in PostgreSQL"""
    if not data:
        return
    
    try:
        # Store data in PostgreSQL
        db_manager.insert_bitcoin_data(
            timestamp=data['timestamp'],
            price_usd=data['usd'],
            market_cap_usd=data.get('usd_market_cap', 0),
            volume_24h_usd=data.get('usd_24h_vol', 0),
            price_change_24h=data.get('usd_24h_change', 0)
        )
        logger.info("Data stored in PostgreSQL successfully")
        
        # Create basic visualization
        create_price_chart()
    except Exception as e:
        logger.error(f"Error storing data: {e}")

def create_price_chart():
    """Create a basic price chart using data from PostgreSQL"""
    try:
        # Get data for the last 24 hours
        data = db_manager.get_recent_bitcoin_data(hours=24)
        
        if data.empty:
            logger.warning("No data available for charting")
            return
        
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Plot price over time
        plt.figure(figsize=(10, 6))
        plt.plot(data['timestamp'], data['price_usd'], marker='o')
        plt.title('Bitcoin Price (USD) Over Time - Last 24 Hours')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the plot
        today = datetime.now().strftime('%Y-%m-%d')
        plt.savefig(f"{CHARTS_DIR}/bitcoin_price_{today}.png")
        plt.close()
        
        logger.info(f"Plot saved to {CHARTS_DIR}/bitcoin_price_{today}.png")
    except Exception as e:
        logger.error(f"Error creating plot: {e}")

def job():
    """Main job to fetch and process data"""
    data = fetch_bitcoin_data()
    process_and_store_data(data)

def main():
    logger.info("Starting Bitcoin data fetcher...")
    
    # Wait for PostgreSQL to be ready
    retry_count = 0
    while retry_count < 5:
        if db_manager.check_connection():
            logger.info("Successfully connected to PostgreSQL")
            # Ensure tables exist
            db_manager.create_tables()
            break
        else:
            retry_count += 1
            wait_time = retry_count * 5
            logger.warning(f"Failed to connect to PostgreSQL. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    if retry_count == 5:
        logger.error("Could not connect to PostgreSQL after multiple attempts. Exiting.")
        return
    
    # Run once immediately
    job()
    
    # Schedule regular runs
    schedule.every(FETCH_INTERVAL).seconds.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()