#!/usr/bin/env python3
"""
Script to fix timestamps in prediction files.
This script updates any outdated timestamps to the current date.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), ''))
import pandas as pd
from datetime import datetime, timedelta
import logging
import yaml
import argparse
from utilities.timestamp_format import format_timestamp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s.%(funcName)s() | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load the application configuration."""
    try:
        config_path = os.path.join('/app/configs/config.yaml')
        # Fall back to local path if /app doesn't exist
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs/config.yaml')
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None

def fix_timestamps(file_path, target_date=None):
    """Fix timestamps in CSV file by updating to the target date."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        # Determine target date
        if target_date is None:
            target_date = datetime.now().date()
        elif isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        if 'timestamp' not in df.columns:
            logger.error(f"No timestamp column found in {file_path}")
            return False
        
        # Convert timestamps to datetime using flexible format detection
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        
        # Store original timestamps for logging
        original_min = df['timestamp'].min()
        original_max = df['timestamp'].max()
        
        # Update timestamps to the target date while preserving time
        def update_date(ts):
            updated_dt = datetime.combine(target_date, ts.time())
            # Format using ISO8601 with T separator
            return format_timestamp(updated_dt, use_t_separator=True)
        
        df['timestamp'] = df['timestamp'].apply(update_date)
        
        # Create backup
        backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        df_original = pd.read_csv(file_path)
        df_original.to_csv(backup_path, index=False)
        logger.info(f"Created backup at {backup_path}")
        
        # Save the updated file
        df.to_csv(file_path, index=False)
        
        logger.info(f"Updated timestamps in {file_path}")
        logger.info(f"Original range: {original_min} to {original_max}")
        logger.info(f"New range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing timestamps in {file_path}: {e}")
        return False

def main():
    """Main function to fix timestamps in prediction files."""
    parser = argparse.ArgumentParser(description="Fix timestamps in prediction files")
    parser.add_argument("--target-date", type=str, help="Target date in YYYY-MM-DD format")
    parser.add_argument("--files", nargs="+", help="Specific files to fix")
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return 1
    
    # Determine target date
    target_date = None
    if args.target_date:
        try:
            target_date = datetime.strptime(args.target_date, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {args.target_date}. Use YYYY-MM-DD")
            return 1
    else:
        target_date = datetime.now().date()
    
    # Determine files to process
    files_to_process = []
    if args.files:
        files_to_process = args.files
    else:
        # Default paths from config
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        
        # Handle Docker vs local paths
        if not os.path.exists(predictions_file):
            predictions_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'data/predictions/instant_predictions.csv'
            )
        if not os.path.exists(metrics_file):
            metrics_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'data/predictions/instant_metrics.csv'
            )
        
        files_to_process = [predictions_file, metrics_file]
    
    # Process each file
    success_count = 0
    for file_path in files_to_process:
        logger.info(f"Processing {file_path}")
        if fix_timestamps(file_path, target_date):
            success_count += 1
    
    logger.info(f"Processed {len(files_to_process)} files, {success_count} successfully updated")
    return 0

if __name__ == "__main__":
    exit(main()) 