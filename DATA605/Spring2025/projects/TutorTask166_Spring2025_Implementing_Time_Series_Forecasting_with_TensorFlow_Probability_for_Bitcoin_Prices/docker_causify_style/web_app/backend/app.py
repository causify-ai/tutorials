#!/usr/bin/env python3
"""
Backend API for Bitcoin Price Dashboard.
Provides endpoints for price data, prediction data, and metrics data.
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
import sys

# Use local unified_config module
from unified_config import get_service_config

# Get service name from environment or use default
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'web_app')

# Load config using unified config parser
config = get_service_config(SERVICE_NAME)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PRICE_FILE = config['data']['raw_data']['instant_data']['file']
PREDICTIONS_FILE = config['data']['predictions']['instant_data']['predictions_file']
METRICS_FILE = config['data']['predictions']['instant_data']['metrics_file']

# Create Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for all routes

def load_csv_safely(file_path, columns=None, skip_rows=1):
    """Safely load CSV data with error handling"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return pd.DataFrame()
            
        # Determine if we should use column names from config or let pandas infer
        if columns:
            df = pd.read_csv(file_path, names=columns, skiprows=skip_rows)
        else:
            df = pd.read_csv(file_path)
        
        # Handle timestamp conversion
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
            
        return df
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()

def filter_last_n_minutes(df, n_minutes):
    """Filter dataframe to last N minutes"""
    if df.empty:
        return df
        
    # Get current time and calculate cutoff
    now = datetime.now()
    cutoff = now - timedelta(minutes=n_minutes)
    
    # Filter dataframe
    filtered_df = df[df['timestamp'] >= cutoff]
    
    return filtered_df

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/price-data')
def get_price_data():
    """API endpoint for price data"""
    try:
        # Load price data
        price_df = load_csv_safely(
            PRICE_FILE,
            columns=config['data_format']['columns']['raw_data']['names']
        )
        
        # Filter to last 60 minutes
        price_df = filter_last_n_minutes(price_df, 60)
        
        # Convert to list of dictionaries for JSON serialization
        result = []
        if not price_df.empty:
            # Convert timestamps to ISO format strings
            price_df['timestamp'] = price_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            result = price_df.to_dict(orient='records')
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in price data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/prediction-data')
def get_prediction_data():
    """API endpoint for prediction data"""
    try:
        # Load prediction data
        pred_df = load_csv_safely(PREDICTIONS_FILE)
        
        # Filter to last 60 minutes
        pred_df = filter_last_n_minutes(pred_df, 60)
        
        # Convert to list of dictionaries for JSON serialization
        result = []
        if not pred_df.empty:
            # Convert timestamps to ISO format strings
            pred_df['timestamp'] = pred_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            result = pred_df.to_dict(orient='records')
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in prediction data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics-data')
def get_metrics_data():
    """API endpoint for metrics data"""
    try:
        # Load metrics data
        metrics_df = load_csv_safely(METRICS_FILE)
        
        # Filter to last 60 minutes
        metrics_df = filter_last_n_minutes(metrics_df, 60)
        
        # Convert to list of dictionaries for JSON serialization
        result = []
        if not metrics_df.empty:
            # Convert timestamps to ISO format strings
            metrics_df['timestamp'] = metrics_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            result = metrics_df.to_dict(orient='records')
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in metrics data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get host and port from config
    host = config['web_app']['backend']['host']
    port = config['web_app']['backend']['port']
    debug = config['web_app']['backend']['debug']
    
    logger.info(f"Starting backend API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug) 