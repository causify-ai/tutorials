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
            # Convert timestamps to ISO format strings without UTC indicator and no milliseconds
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
            # Convert timestamps to ISO format strings without UTC indicator and no milliseconds
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
        
        # Calculate recent metrics statistics (last 30 minutes)
        if not metrics_df.empty and 'actual_error' in metrics_df.columns:
            # Convert timestamp to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(metrics_df['timestamp']):
                metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
            
            # Get the most recent timestamp
            max_time = metrics_df['timestamp'].max()
            # Calculate the time window (30 minutes ago)
            min_time = max_time - pd.Timedelta(minutes=30)
            
            # Filter to last 30 minutes
            recent_metrics_df = metrics_df[metrics_df['timestamp'] >= min_time]
            
            if not recent_metrics_df.empty:
                # Calculate statistics on the recent data
                recent_avg_error = recent_metrics_df['actual_error'].mean()
                recent_mae = recent_metrics_df['actual_error'].abs().mean()
                
                logger.info(f"Recent metrics statistics - Avg Error: {recent_avg_error:.2f}, MAE: {recent_mae:.2f}")
        
        # Keep all available metrics data for error distribution chart
        # Don't filter by time window for metrics to ensure enough data for distribution
        
        # Load prediction data to calculate actual error if needed
        if 'actual_error' not in metrics_df.columns and not metrics_df.empty:
            try:
                pred_df = load_csv_safely(PREDICTIONS_FILE)
                price_df = load_csv_safely(PRICE_FILE)
                
                if not pred_df.empty and not price_df.empty:
                    logger.info("Calculating actual_error field for metrics")
                    # Join predictions and actual prices
                    merged_df = pd.merge_asof(
                        pred_df.sort_values('timestamp'),
                        price_df.sort_values('timestamp'),
                        on='timestamp',
                        direction='nearest',
                        tolerance=pd.Timedelta('1 minute')
                    )
                    
                    if not merged_df.empty:
                        # Calculate actual error
                        merged_df['actual_error'] = merged_df['predicted_price'] - merged_df['price']
                        
                        # Join with metrics
                        metrics_df = pd.merge_asof(
                            metrics_df.sort_values('timestamp'),
                            merged_df[['timestamp', 'actual_error']],
                            on='timestamp',
                            direction='nearest',
                            tolerance=pd.Timedelta('1 minute')
                        )
            except Exception as e:
                logger.error(f"Error calculating actual_error: {e}")
        
        # Calculate final metrics statistics
        if not metrics_df.empty and 'actual_error' in metrics_df.columns:
            # Calculate statistics on all data (for comparison with recent)
            avg_error = metrics_df['actual_error'].mean()
            mae = metrics_df['actual_error'].abs().mean()
            
            logger.info(f"Final metrics statistics - Avg Error: {avg_error:.2f}, MAE: {mae:.2f}")
            
            # Add a metadata record with the recent metrics
            if 'recent_avg_error' in locals() and 'recent_mae' in locals():
                metadata_record = {
                    'timestamp': metrics_df['timestamp'].max().strftime('%Y-%m-%dT%H:%M:%S'),
                    'is_metadata': True,
                    'recent_avg_error': float(f"{recent_avg_error:.2f}"),
                    'recent_mae': float(f"{recent_mae:.2f}"),
                    'total_avg_error': float(f"{avg_error:.2f}"),
                    'total_mae': float(f"{mae:.2f}")
                }
                
                # Convert metrics_df to list of dictionaries
                result = metrics_df.to_dict(orient='records')
                # Add metadata record at the beginning
                result.insert(0, metadata_record)
            else:
                result = metrics_df.to_dict(orient='records')
        else:
            result = metrics_df.to_dict(orient='records')
        
        # Convert timestamps to ISO format strings
        for record in result:
            if 'timestamp' in record and not isinstance(record['timestamp'], str):
                record['timestamp'] = record['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
        
        logger.info(f"Returning {len(metrics_df)} metrics data points")
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