import pandas as pd
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

def load_and_filter_data(config, predictions_file, metrics_file, raw_data_file):
    """
    Unified data loader for all dashboards. Returns (predictions, metrics, raw_data) DataFrames.
    - Filters to last N seconds (from config)
    - Drops rows with missing/invalid values
    - Ensures all arrays are aligned by timestamp
    """
    # Define date parser function
    def parse_date(date_str):
        try:
            return pd.to_datetime(date_str, format=config['data_format']['timestamp']['format'])
        except:
            return pd.NaT

    # Load predictions
    predictions = pd.read_csv(
        predictions_file,
        names=config['data_format']['columns']['predictions']['names'],
        skiprows=1,
        parse_dates=['timestamp'],
        date_parser=parse_date
    )
    # Load metrics
    metrics = pd.read_csv(
        metrics_file,
        names=config['data_format']['columns']['metrics']['names'],
        skiprows=1,
        parse_dates=['timestamp'],
        date_parser=parse_date
    )
    # Load raw data
    raw_data = pd.read_csv(
        raw_data_file,
        names=config['data_format']['columns']['raw_data']['names'],
        skiprows=1,
        parse_dates=['timestamp'],
        date_parser=parse_date
    )
    # Ensure proper data types
    for df, col_config in [
        (predictions, config['data_format']['columns']['predictions']['dtypes']),
        (metrics, config['data_format']['columns']['metrics']['dtypes']),
        (raw_data, config['data_format']['columns']['raw_data']['dtypes'])
    ]:
        for col, dtype in col_config.items():
            if col in df.columns:
                if dtype == 'datetime64[ns]':
                    df[col] = pd.to_datetime(df[col], format=config['data_format']['timestamp']['format'])
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
    # Filter to last time_window seconds (from config)
    time_window = timedelta(seconds=config['dashboard']['plot_settings']['time_window'])
    cutoff_time = datetime.now() - time_window
    predictions = predictions[predictions['timestamp'] >= cutoff_time]
    metrics = metrics[metrics['timestamp'] >= cutoff_time]
    raw_data = raw_data[raw_data['timestamp'] >= cutoff_time]
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
    # Align by timestamp (inner join on timestamp)
    common_timestamps = set(raw_data['timestamp']) & set(predictions['timestamp'])
    if len(common_timestamps) > 0:
        raw_data = raw_data[raw_data['timestamp'].isin(common_timestamps)]
        predictions = predictions[predictions['timestamp'].isin(common_timestamps)]
        metrics = metrics[metrics['timestamp'].isin(common_timestamps)]
    return predictions, metrics, raw_data 