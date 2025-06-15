import pandas as pd
from datetime import datetime, timedelta
import os
from utilities.logger import get_logger
import time
import traceback
from utilities.timestamp_format import parse_timestamp

logger = get_logger(__name__)

def robust_parse_dates(date_str, config_format):
    """Try parsing with config format, then fallback to space format."""
    try:
        return datetime.strptime(date_str, config_format)
    except Exception:
        try:
            # Fallback: replace T with space and try again
            alt_format = config_format.replace('T', ' ')
            return datetime.strptime(date_str, alt_format)
        except Exception:
            logger.warning(f"Could not parse timestamp: {date_str}")
            return pd.NaT

def load_and_filter_data(config, predictions_file, metrics_file, raw_data_file):
    """
    Unified data loader for all dashboards. Returns (predictions, metrics, raw_data) DataFrames.
    - Filters to last N seconds (from config)
    - Drops rows with missing/invalid values
    - Ensures all arrays are aligned by timestamp
    """
    try:
        logger.info(f"Loading data from files:")
        logger.info(f"  - Predictions: {predictions_file}")
        logger.info(f"  - Metrics: {metrics_file}")
        logger.info(f"  - Raw data: {raw_data_file}")

        # Check if files exist
        for file_path in [predictions_file, metrics_file, raw_data_file]:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None, None, None

        # Helper for robust date parsing
        def parse_dates_col(col):
            return [parse_timestamp(x) for x in col]

        # Load predictions with retry
        max_retries = 3
        retry_delay = 1  # seconds
        
        predictions = None
        for attempt in range(max_retries):
            try:
                predictions = pd.read_csv(
                    predictions_file,
                    names=config['data_format']['columns']['predictions']['names'],
                    skiprows=1,
                    on_bad_lines='skip'  # Skip bad lines instead of failing
                )
                predictions['timestamp'] = parse_dates_col(predictions['timestamp'])
                logger.info(f"Successfully loaded predictions with {len(predictions)} rows")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt+1}/{max_retries} failed to load predictions: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to load predictions after {max_retries} attempts: {e}\n{traceback.format_exc()}")
                    predictions = pd.DataFrame(columns=config['data_format']['columns']['predictions']['names'])
                time.sleep(retry_delay)
        
        # Load metrics with retry
        metrics = None
        for attempt in range(max_retries):
            try:
                metrics = pd.read_csv(
                    metrics_file,
                    names=config['data_format']['columns']['metrics']['names'],
                    skiprows=1,
                    on_bad_lines='skip'  # Skip bad lines instead of failing
                )
                metrics['timestamp'] = parse_dates_col(metrics['timestamp'])
                logger.info(f"Successfully loaded metrics with {len(metrics)} rows")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt+1}/{max_retries} failed to load metrics: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to load metrics after {max_retries} attempts: {e}\n{traceback.format_exc()}")
                    metrics = pd.DataFrame(columns=config['data_format']['columns']['metrics']['names'])
                time.sleep(retry_delay)
        
        # Load raw data with retry
        raw_data = None
        for attempt in range(max_retries):
            try:
                raw_data = pd.read_csv(
                    raw_data_file,
                    names=config['data_format']['columns']['raw_data']['names'],
                    skiprows=1,
                    on_bad_lines='skip'  # Skip bad lines instead of failing
                )
                raw_data['timestamp'] = parse_dates_col(raw_data['timestamp'])
                logger.info(f"Successfully loaded raw data with {len(raw_data)} rows")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt+1}/{max_retries} failed to load raw data: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to load raw data after {max_retries} attempts: {e}\n{traceback.format_exc()}")
                    raw_data = pd.DataFrame(columns=config['data_format']['columns']['raw_data']['names'])
                time.sleep(retry_delay)

        # Ensure all dataframes exist
        if predictions is None:
            predictions = pd.DataFrame(columns=config['data_format']['columns']['predictions']['names'])
        if metrics is None:
            metrics = pd.DataFrame(columns=config['data_format']['columns']['metrics']['names'])
        if raw_data is None:
            raw_data = pd.DataFrame(columns=config['data_format']['columns']['raw_data']['names'])

        # Ensure proper data types
        for df, col_config in [
            (predictions, config['data_format']['columns']['predictions']['dtypes']),
            (metrics, config['data_format']['columns']['metrics']['dtypes']),
            (raw_data, config['data_format']['columns']['raw_data']['dtypes'])
        ]:
            for col, dtype in col_config.items():
                if col in df.columns:
                    if dtype == 'datetime64[ns]':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    else:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

        # Filter to last time_window seconds (from config)
        time_window = timedelta(seconds=config['dashboard']['plot_settings']['time_window'])
        cutoff_time = datetime.now() - time_window
        
        # Drop NaN timestamps before filtering
        predictions = predictions.dropna(subset=['timestamp'])
        metrics = metrics.dropna(subset=['timestamp'])
        raw_data = raw_data.dropna(subset=['timestamp'])
        
        # Filter by time
        predictions = predictions[predictions['timestamp'] >= cutoff_time]
        metrics = metrics[metrics['timestamp'] >= cutoff_time]
        raw_data = raw_data[raw_data['timestamp'] >= cutoff_time]

        logger.info(f"After time window filter:")
        logger.info(f"  - Predictions: {len(predictions)} rows")
        logger.info(f"  - Metrics: {len(metrics)} rows")
        logger.info(f"  - Raw data: {len(raw_data)} rows")

        # Drop rows with missing/invalid values
        predictions = predictions.dropna()
        metrics = metrics.dropna()
        raw_data = raw_data.dropna()

        # Sort by timestamp
        predictions = predictions.sort_values('timestamp')
        metrics = metrics.sort_values('timestamp')
        raw_data = raw_data.sort_values('timestamp')

        # Limit to max_points
        max_points = config['dashboard']['plot_settings']['max_points']
        predictions = predictions.tail(max_points)
        metrics = metrics.tail(max_points)
        raw_data = raw_data.tail(max_points)

        # Check if any dataframes are empty after processing
        if len(raw_data) == 0:
            logger.warning("No valid raw data after filtering")
        if len(predictions) == 0:
            logger.warning("No valid predictions after filtering")
        if len(metrics) == 0:
            logger.warning("No valid metrics after filtering")

        return predictions, metrics, raw_data

    except Exception as e:
        logger.error(f"Error in load_and_filter_data: {e}\n{traceback.format_exc()}")
        return None, None, None 