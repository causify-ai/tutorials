import os
import time
import json
import threading
import requests
import pandas as pd
import schedule
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask, Response
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST

from db_manager import DatabaseManager
from utils import setup_logging
from advanced_analytics import perform_time_series_analysis, detect_price_anomalies

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

# Set up Prometheus metrics
REQUESTS_TOTAL = Counter('bitcoin_fetcher_requests_total', 'Total number of requests to Bitcoin API')
REQUESTS_FAILED = Counter('bitcoin_fetcher_requests_failed', 'Number of failed requests to Bitcoin API')
BTC_PRICE = Gauge('bitcoin_price_usd', 'Current Bitcoin price in USD')
BTC_MARKET_CAP = Gauge('bitcoin_market_cap_usd', 'Current Bitcoin market cap in USD')
BTC_VOLUME = Gauge('bitcoin_volume_24h_usd', 'Bitcoin 24h trading volume in USD')
BTC_PRICE_CHANGE = Gauge('bitcoin_price_change_24h', 'Bitcoin 24h price change percentage')
REQUEST_DURATION = Histogram('bitcoin_request_duration_seconds', 'Time spent processing requests')
DATA_POINTS = Counter('bitcoin_data_points_stored', 'Number of data points stored in the database')
ANOMALIES_DETECTED = Counter('bitcoin_anomalies_detected', 'Number of price anomalies detected')

# Start the Flask app for Prometheus metrics
app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def start_metrics_server():
    """Start the metrics server in a separate thread"""
    logger.info("Starting Prometheus metrics server on port 8000")
    app.run(host='0.0.0.0', port=8000)

def fetch_bitcoin_data():
    """Fetch Bitcoin data from CoinGecko API"""
    REQUESTS_TOTAL.inc()
    start_time = time.time()
    
    try:
        logger.info("Fetching Bitcoin data...")
        response = requests.get(API_URL)
        response.raise_for_status()
        
        data = response.json()
        timestamp = datetime.now()
        
        bitcoin_data = data.get('bitcoin', {})
        if not bitcoin_data:
            logger.error("No Bitcoin data found in the response")
            REQUESTS_FAILED.inc()
            return None
        
        # Add timestamp to the data
        bitcoin_data['timestamp'] = timestamp
        
        # Update Prometheus metrics
        BTC_PRICE.set(bitcoin_data.get('usd', 0))
        BTC_MARKET_CAP.set(bitcoin_data.get('usd_market_cap', 0))
        BTC_VOLUME.set(bitcoin_data.get('usd_24h_vol', 0))
        BTC_PRICE_CHANGE.set(bitcoin_data.get('usd_24h_change', 0))
        
        logger.info(f"Data fetched successfully: {bitcoin_data}")
        return bitcoin_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        REQUESTS_FAILED.inc()
        return None
    
    finally:
        REQUEST_DURATION.observe(time.time() - start_time)

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
        DATA_POINTS.inc()
        
        # Create visualizations and perform analysis
        create_visualizations()
        
        # Run anomaly detection
        recent_data = db_manager.get_recent_bitcoin_data(hours=24)
        if not recent_data.empty and len(recent_data) > 10:  # Need enough data points
            anomalies = detect_price_anomalies(recent_data)
            if anomalies['has_anomaly']:
                logger.warning(f"Price anomaly detected! {anomalies['message']}")
                ANOMALIES_DETECTED.inc()
    
    except Exception as e:
        logger.error(f"Error processing data: {e}")

def create_visualizations():
    """Create various visualizations based on the data"""
    try:
        # Get data for different time periods
        data_24h = db_manager.get_recent_bitcoin_data(hours=24)
        data_7d = db_manager.get_recent_bitcoin_data(hours=24*7)
        
        if data_24h.empty:
            logger.warning("No data available for charting")
            return
            
        # Convert timestamp to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(data_24h['timestamp']):
            data_24h['timestamp'] = pd.to_datetime(data_24h['timestamp'])
            
        if not data_7d.empty and not pd.api.types.is_datetime64_any_dtype(data_7d['timestamp']):
            data_7d['timestamp'] = pd.to_datetime(data_7d['timestamp'])
        
        # 1. Price chart for the last 24 hours
        plt.figure(figsize=(10, 6))
        plt.plot(data_24h['timestamp'], data_24h['price_usd'], marker='o', linestyle='-', color='blue')
        plt.title('Bitcoin Price (USD) - Last 24 Hours')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        today = datetime.now().strftime('%Y-%m-%d')
        plt.savefig(f"{CHARTS_DIR}/bitcoin_price_24h_{today}.png")
        plt.close()
        
        # 2. Week price chart if we have enough data
        if not data_7d.empty and len(data_7d) > 10:
            plt.figure(figsize=(12, 6))
            plt.plot(data_7d['timestamp'], data_7d['price_usd'], marker='.', linestyle='-', color='green')
            plt.title('Bitcoin Price (USD) - Last 7 Days')
            plt.xlabel('Time')
            plt.ylabel('Price (USD)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{CHARTS_DIR}/bitcoin_price_7d_{today}.png")
            plt.close()
            
            # 3. Time series analysis and forecast
            if len(data_7d) >= 30:  # Need enough data for forecasting
                forecast_result = perform_time_series_analysis(data_7d)
                if forecast_result and 'forecast_fig' in forecast_result:
                    forecast_result['forecast_fig'].savefig(f"{CHARTS_DIR}/bitcoin_forecast_{today}.png")
                    plt.close(forecast_result['forecast_fig'])
        
        # 4. Market cap vs price plot
        if len(data_24h) > 5:
            plt.figure(figsize=(10, 6))
            plt.scatter(data_24h['market_cap_usd'], data_24h['price_usd'], alpha=0.7)
            plt.title('Bitcoin Price vs Market Cap - Last 24 Hours')
            plt.xlabel('Market Cap (USD)')
            plt.ylabel('Price (USD)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{CHARTS_DIR}/btc_price_vs_mcap_{today}.png")
            plt.close()
            
        logger.info(f"Visualizations created successfully in {CHARTS_DIR}")
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")

def job():
    """Main job to fetch and process data"""
    data = fetch_bitcoin_data()
    process_and_store_data(data)

def main():
    logger.info("Starting Bitcoin data fetcher...")
    
    # Start the metrics server
    metrics_thread = threading.Thread(target=start_metrics_server, daemon=True)
    metrics_thread.start()
    
    # Wait for PostgreSQL to be ready
    retry_count = 0
    max_retries = 10
    while retry_count < max_retries:
        if db_manager.check_connection():
            logger.info("Successfully connected to PostgreSQL")
            # Ensure tables exist
            db_manager.create_tables()
            break
        else:
            retry_count += 1
            wait_time = retry_count * 5
            logger.warning(f"Failed to connect to PostgreSQL. Retrying in {wait_time} seconds... ({retry_count}/{max_retries})")
            time.sleep(wait_time)
    
    if retry_count == max_retries:
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