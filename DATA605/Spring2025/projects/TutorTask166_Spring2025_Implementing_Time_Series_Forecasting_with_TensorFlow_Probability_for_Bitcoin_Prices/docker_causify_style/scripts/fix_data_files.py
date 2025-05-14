#!/usr/bin/env python3
"""
Script to fix malformed data files causing errors in the Bitcoin forecast application.
This script cleans up CSV files that might have inconsistent column counts or other issues.
"""
import pandas as pd
import os
import yaml
import logging
import sys
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file."""
    try:
        with open('/app/configs/config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None

def fix_csv_file(file_path, column_names, validate_timestamps=False, price_df=None, pred_df=None):
    """Fix a CSV file with inconsistent columns or other issues."""
    logger.info(f"Attempting to fix file: {file_path}")
    
    if not os.path.exists(file_path):
        logger.warning(f"File does not exist: {file_path}")
        return False
        
    # Create backup of original file
    backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        with open(file_path, 'r') as src:
            with open(backup_path, 'w') as dst:
                dst.write(src.read())
        logger.info(f"Created backup file: {backup_path}")
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False
    
    # Try to read the file with pandas, allowing bad lines to be skipped
    try:
        # First try to read header
        header_df = pd.read_csv(file_path, nrows=1)
        detected_columns = header_df.columns.tolist()
        logger.info(f"Detected header: {detected_columns}")
        
        # Read data and skip bad lines
        df = pd.read_csv(
            file_path, 
            names=column_names,
            skiprows=1,  # Skip the original header
            on_bad_lines='skip'  # Skip problematic rows
        )
        
        # Filter out any rows with incorrect number of columns
        expected_cols = len(column_names)
        logger.info(f"Expected columns: {expected_cols}, got {len(df.columns)}")
        
        # Ensure all required columns are present
        for col in column_names:
            if col not in df.columns:
                df[col] = None
                
        # Convert timestamp column if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # Drop rows with invalid timestamps
            df = df.dropna(subset=['timestamp'])
            
        # Convert numeric columns
        numeric_cols = [col for col in df.columns if col != 'timestamp']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Drop rows with all NaN values (except timestamp)
        df = df.dropna(subset=numeric_cols, how='all')
            
        # Sort by timestamp if applicable
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')

        # Special handling for metrics file - validate timestamp alignment
        if validate_timestamps and price_df is not None and pred_df is not None and 'mae' in df.columns:
            logger.info("Performing timestamp validation for metrics file")
            
            # Round timestamps to seconds for comparison
            df['timestamp_rounded'] = df['timestamp'].dt.floor('S')
            price_df['timestamp_rounded'] = price_df['timestamp'].dt.floor('S')
            pred_df['timestamp_rounded'] = pred_df['timestamp'].dt.floor('S')
            
            # Create sets of timestamps
            price_timestamps = set(price_df['timestamp_rounded'])
            pred_timestamps = set(pred_df['timestamp_rounded'])
            
            # Find timestamps that exist in both price and prediction data
            valid_timestamps = price_timestamps.intersection(pred_timestamps)
            
            # Filter metrics dataframe to only include timestamps with both actual and predicted data
            original_len = len(df)
            df = df[df['timestamp_rounded'].isin(valid_timestamps)]
            filtered_len = len(df)
            
            # Remove temporary column
            df = df.drop('timestamp_rounded', axis=1)
            
            logger.info(f"Timestamp validation: kept {filtered_len} of {original_len} records with valid timestamps")
            
            # Detect and fix corrupted metrics entries (same value for all metrics)
            if 'std' in df.columns and 'mae' in df.columns and 'rmse' in df.columns:
                # Check for rows where all metrics have the same value (likely corrupted)
                corrupt_rows = df[(df['std'] == df['mae']) & (df['mae'] == df['rmse']) & (df['mae'] > 1000)]
                if not corrupt_rows.empty:
                    logger.warning(f"Found {len(corrupt_rows)} corrupt metric entries (identical value in all columns)")
                    # Remove corrupt rows
                    df = df[~df.index.isin(corrupt_rows.index)]
                    logger.info(f"Removed {len(corrupt_rows)} corrupt metric entries")
            
        # Write back the clean data to the original file
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully fixed and rewrote file with {len(df)} valid rows")
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix file {file_path}: {e}\n{traceback.format_exc()}")
        # Try to restore from backup
        try:
            with open(backup_path, 'r') as src:
                with open(file_path, 'w') as dst:
                    dst.write(src.read())
            logger.info(f"Restored from backup due to error")
        except Exception as restore_err:
            logger.error(f"Failed to restore from backup: {restore_err}")
        return False

def fix_all_data_files():
    """Fix all data files referenced in the config."""
    config = load_config()
    if not config:
        logger.error("Cannot proceed without config")
        return False
        
    success = True
    
    # Fix raw data file
    raw_data_file = config['data']['raw_data']['instant_data']['file']
    raw_data_columns = config['data_format']['columns']['raw_data']['names']
    if not fix_csv_file(raw_data_file, raw_data_columns):
        success = False
        
    # Fix predictions file
    predictions_file = config['data']['predictions']['instant_data']['predictions_file']
    predictions_columns = config['data_format']['columns']['predictions']['names']
    if not fix_csv_file(predictions_file, predictions_columns):
        success = False
        
    # Load price and prediction data for metrics validation
    price_df = None
    pred_df = None
    try:
        # Load the fixed files to validate metrics timestamps
        if os.path.exists(raw_data_file):
            price_df = pd.read_csv(raw_data_file)
            if 'timestamp' in price_df.columns:
                price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], errors='coerce')
                
        if os.path.exists(predictions_file):
            pred_df = pd.read_csv(predictions_file)
            if 'timestamp' in pred_df.columns:
                pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'], errors='coerce')
                
        logger.info(f"Loaded price data: {len(price_df) if price_df is not None else 0} rows")
        logger.info(f"Loaded prediction data: {len(pred_df) if pred_df is not None else 0} rows")
    except Exception as e:
        logger.error(f"Error loading data for metrics validation: {e}")
        
    # Fix metrics file with timestamp validation
    metrics_file = config['data']['predictions']['instant_data']['metrics_file']
    metrics_columns = config['data_format']['columns']['metrics']['names']
    if not fix_csv_file(metrics_file, metrics_columns, validate_timestamps=True, price_df=price_df, pred_df=pred_df):
        success = False
        
    return success

def fix_metrics_file_only():
    """Fix only the metrics file, focusing on timestamp alignment and data quality."""
    config = load_config()
    if not config:
        logger.error("Cannot proceed without config")
        return False
        
    # Load price and prediction data for metrics validation
    price_df = None
    pred_df = None
    try:
        # Load the raw data files to validate metrics timestamps
        raw_data_file = config['data']['raw_data']['instant_data']['file']
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        
        if os.path.exists(raw_data_file):
            price_df = pd.read_csv(raw_data_file)
            if 'timestamp' in price_df.columns:
                price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], errors='coerce')
                
        if os.path.exists(predictions_file):
            pred_df = pd.read_csv(predictions_file)
            if 'timestamp' in pred_df.columns:
                pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'], errors='coerce')
                
        logger.info(f"Loaded price data: {len(price_df) if price_df is not None else 0} rows")
        logger.info(f"Loaded prediction data: {len(pred_df) if pred_df is not None else 0} rows")
    except Exception as e:
        logger.error(f"Error loading data for metrics validation: {e}")
        return False
        
    # Fix metrics file with timestamp validation
    metrics_file = config['data']['predictions']['instant_data']['metrics_file']
    metrics_columns = config['data_format']['columns']['metrics']['names']
    
    success = fix_csv_file(metrics_file, metrics_columns, validate_timestamps=True, price_df=price_df, pred_df=pred_df)
    return success

def main():
    """Main function to execute the script."""
    logger.info("Starting data file repair script")
    try:
        # Check if we only want to fix metrics
        if len(sys.argv) > 1 and sys.argv[1] == "--metrics-only":
            logger.info("Running in metrics-only mode")
            success = fix_metrics_file_only()
        else:
            # Run full data fix
            success = fix_all_data_files()
            
        if success:
            logger.info("Successfully repaired all data files")
            return 0
        else:
            logger.warning("Some files could not be repaired")
            return 1
    except Exception as e:
        logger.error(f"Unhandled exception in repair script: {e}\n{traceback.format_exc()}")
        return 2

if __name__ == "__main__":
    sys.exit(main()) 