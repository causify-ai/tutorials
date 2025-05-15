"""
template_utils.py

This file contains utility functions that support the Bitcoin price forecasting application.

- Functions are organized by category (timestamp handling, logging, data loading, etc.)
- Each function has proper documentation with parameter types and descriptions
- This centralized approach helps keep the codebase clean, modular, and easier to debug
"""

import pandas as pd
import numpy as np
import logging
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Union, Optional, Any

# -----------------------------------------------------------------------------
# Logging Functions
# -----------------------------------------------------------------------------

def get_logger(name: str, log_level: Optional[Union[str, int]] = None) -> logging.Logger:
    """
    Get a logger with the specified name and log level.
    
    :param name: name of the logger
    :param log_level: log level (e.g., 'INFO', 'DEBUG', etc.) or None to use default
    
    :return: configured logger instance
    """
    # Set default log level to INFO if not specified
    if log_level is None:
        level = logging.INFO
    elif isinstance(log_level, str):
        # Convert string log level to logging constant
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        # Use the provided level directly
        level = log_level
    
    # Configure root logger if not already configured
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s.%(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get the logger and set its level
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    return logger

# Default logger for this module
logger = get_logger(__name__)

# -----------------------------------------------------------------------------
# Timestamp Handling Functions
# -----------------------------------------------------------------------------

def to_iso8601(ts: Union[str, datetime, Any]) -> str:
    """
    Convert a timestamp to ISO8601 format.
    
    :param ts: timestamp as string, datetime object, or other format
    
    :return: formatted ISO8601 string
    """
    # If already a string, just return
    if isinstance(ts, str):
        return ts
    # If it's a datetime, format it
    if hasattr(ts, 'isoformat'):
        return ts.isoformat(timespec='seconds').replace('+00:00', 'Z')
    # Fallback: convert to string
    return str(ts)

def format_timestamp(ts: Union[str, datetime, int, float], use_t_separator: bool = True) -> Optional[str]:
    """
    Format timestamp consistently to ISO8601 format with T or space separator.
    
    :param ts: timestamp as string, datetime, or numeric (epoch)
    :param use_t_separator: if True, use 'T' separator, otherwise use space
    
    :return: formatted timestamp string in ISO8601 format
    """
    if isinstance(ts, str):
        # Parse string to datetime 
        ts = parse_timestamp(ts)
    elif isinstance(ts, (int, float)):
        # Convert epoch to datetime
        ts = datetime.utcfromtimestamp(ts)
        
    if ts is None:
        return None
        
    # Format with T separator or space based on preference
    format_string = "%Y-%m-%dT%H:%M:%S" if use_t_separator else "%Y-%m-%d %H:%M:%S"
    return ts.strftime(format_string)

def parse_timestamp(s: Union[str, int, float]) -> Optional[datetime]:
    """
    Parse ISO8601 string or int/float epoch to datetime (UTC).
    
    :param s: timestamp string, int, or float to parse
    
    :return: datetime object or None if parsing fails
    """
    if isinstance(s, (int, float)):
        return datetime.utcfromtimestamp(s)
    try:
        return pd.to_datetime(s, utc=True).to_pydatetime().replace(tzinfo=None)
    except Exception:
        # fallback: try as epoch
        try:
            return datetime.utcfromtimestamp(float(s))
        except Exception:
            return None

def robust_parse_dates(date_str: str, config_format: str) -> Union[datetime, pd.NaT]:
    """
    Try parsing dates with config format, then fallback to space format.
    
    :param date_str: date string to parse
    :param config_format: format string to use for parsing
    
    :return: parsed datetime or pd.NaT if parsing fails
    """
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

# -----------------------------------------------------------------------------
# Price Formatting Functions
# -----------------------------------------------------------------------------

def normalize_price(value: Union[float, str, int]) -> float:
    """
    Convert price to USD, rounded to 2 decimal places.
    
    :param value: price value to normalize
    
    :return: normalized price as float with 2 decimal places
    """
    return round(float(value), 2)

def usd_to_display_str(value: Union[float, str, int]) -> str:
    """
    Convert USD price to display string, e.g., 99561.32 -> '99.56k'.
    
    :param value: price value to format
    
    :return: formatted price string with appropriate scaling
    """
    try:
        value = round(float(value), 2)
        if value >= 1000:
            return f"{value/1000:.2f}k"
        return f"{value:.2f}"
    except (ValueError, TypeError):
        # Return a safe default if conversion fails
        return "N/A"

# -----------------------------------------------------------------------------
# Data Loading Functions
# -----------------------------------------------------------------------------

def load_and_filter_data(config: Dict, 
                         predictions_file: str, 
                         metrics_file: str, 
                         raw_data_file: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Unified data loader for all dashboards. Returns (predictions, metrics, raw_data) DataFrames.
    
    :param config: application configuration dictionary
    :param predictions_file: path to predictions CSV file
    :param metrics_file: path to metrics CSV file
    :param raw_data_file: path to raw data CSV file
    
    :return: tuple of (predictions, metrics, raw_data) DataFrames
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

# -----------------------------------------------------------------------------
# Data Repair Functions
# -----------------------------------------------------------------------------

def fix_csv_file(file_path: str, 
                column_names: List[str], 
                validate_timestamps: bool = False, 
                price_df: Optional[pd.DataFrame] = None, 
                pred_df: Optional[pd.DataFrame] = None) -> bool:
    """
    Fix a CSV file with inconsistent columns or other issues.
    
    :param file_path: path to the CSV file to fix
    :param column_names: list of expected column names
    :param validate_timestamps: whether to validate timestamps against other dataframes
    :param price_df: price dataframe for timestamp validation
    :param pred_df: predictions dataframe for timestamp validation
    
    :return: True if fix was successful, False otherwise
    """
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

# -----------------------------------------------------------------------------
# Model Evaluation Functions
# -----------------------------------------------------------------------------

def evaluate_prediction(actual_price: float, 
                       prediction: float, 
                       timestamp: Optional[Union[str, datetime]] = None,
                       recent_errors: Optional[List[float]] = None,
                       anomaly_threshold: float = 3.0) -> Dict[str, Any]:
    """
    Evaluate a prediction against the actual price and track errors.
    
    :param actual_price: actual observed price
    :param prediction: predicted price
    :param timestamp: optional timestamp for the prediction
    :param recent_errors: list of recent absolute errors (for z-score calculation)
    :param anomaly_threshold: z-score threshold for anomaly detection
    
    :return: dictionary of evaluation metrics
    """
    try:
        # Calculate absolute error
        error = actual_price - prediction
        abs_error = abs(error)
        
        # Calculate percentage error
        pct_error = (error / actual_price) * 100 if actual_price != 0 else float('inf')
        
        # Calculate z-score of current error if recent errors are provided
        z_score = 0
        is_anomaly = False
        
        if recent_errors is not None and len(recent_errors) > 5:
            mean_error = np.mean(recent_errors)
            std_error = np.std(recent_errors) + 1e-8  # Avoid division by zero
            z_score = (abs_error - mean_error) / std_error
            is_anomaly = z_score > anomaly_threshold
        
        # Round metrics to 2 decimal places
        abs_error = round(abs_error, 2)
        pct_error = round(pct_error, 2)
        z_score = round(z_score, 2)
        
        return {
            'absolute_error': abs_error,
            'percentage_error': pct_error,
            'z_score': z_score,
            'is_anomaly': is_anomaly,
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"Error evaluating prediction: {e}\n{traceback.format_exc()}")
        return {
            'absolute_error': float('nan'),
            'percentage_error': float('nan'),
            'z_score': float('nan'),
            'is_anomaly': False,
            'timestamp': timestamp
        }

# -----------------------------------------------------------------------------
# Data Preprocessing Functions
# -----------------------------------------------------------------------------

def preprocess_price_data(data: Union[np.ndarray, pd.Series, List[float]]) -> np.ndarray:
    """
    Preprocess time series data with advanced techniques.
    
    :param data: raw price time series data
    
    :return: preprocessed data suitable for model training
    """
    try:
        # Convert to numpy array if needed
        if isinstance(data, pd.Series):
            data = data.values
        elif isinstance(data, list):
            data = np.array(data)
        
        if len(data.shape) == 0:
            data = np.array([data])
        
        # Check for very short sequences
        if len(data) < 5:
            logger.warning(f"Warning: Short data sequence ({len(data)} points). Minimal preprocessing applied.")
            return data
        
        # Create pandas Series for easier manipulation
        series = pd.Series(data)
        
        # Check for outliers using Z-score
        z_scores = (series - series.mean()) / series.std()
        abs_z_scores = np.abs(z_scores)
        outlier_indices = np.where(abs_z_scores > 3)[0]
        
        # If outliers found, replace with median of nearby points
        if len(outlier_indices) > 0:
            logger.info(f"Found {len(outlier_indices)} outliers in data")
            for idx in outlier_indices:
                # Use local median (5 points before and after if available)
                start_idx = max(0, idx - 5)
                end_idx = min(len(series), idx + 6)
                local_values = series.iloc[start_idx:end_idx].copy()
                # Remove the outlier itself from the local values
                if idx >= start_idx and idx < end_idx:
                    local_values = local_values.drop(local_values.index[idx - start_idx])
                if not local_values.empty:
                    series.iloc[idx] = local_values.median()
        
        return series.values
            
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}\n{traceback.format_exc()}")
        # Return original data as fallback
        return data

# -----------------------------------------------------------------------------
# Time Series Forecasting Functions
# -----------------------------------------------------------------------------

def adaptive_forecast(time_series: np.ndarray, 
                     forecast_horizon: int = 1, 
                     use_trend_adjustment: bool = True,
                     trend_factor: float = 0.3) -> Tuple[float, float, float]:
    """
    Generate forecasts for future timesteps with adaptive trend adjustment.
    
    :param time_series: historical time series data as numpy array
    :param forecast_horizon: number of steps to forecast ahead
    :param use_trend_adjustment: whether to apply trend-based adjustments
    :param trend_factor: weight factor for trend adjustment (0.0-1.0)
    
    :return: tuple of (mean forecast, lower bound, upper bound)
    """
    try:
        if len(time_series) < 2:
            raise ValueError("Time series must have at least 2 data points")
            
        # Use the last value as the base prediction
        mean_val = float(time_series[-1])
        
        # Add trend-based adjustment to improve short-term forecasts
        if use_trend_adjustment and len(time_series) >= 3:
            # Calculate recent trend from the last few observations
            recent_data = time_series[-3:]
            
            # Calculate average rate of change
            diffs = np.diff(recent_data)
            avg_change = np.mean(diffs)
            
            # Apply the adjustment to the forecast
            trend_adjustment = avg_change * trend_factor
            mean_val += trend_adjustment * forecast_horizon
            
        # Calculate standard deviation for confidence interval
        if len(time_series) >= 5:
            std = float(np.std(time_series[-5:]))
        else:
            std = float(mean_val * 0.005)  # 0.5% of mean as std
        
        # Create confidence interval (95%)
        lower_val = mean_val - 1.96 * std
        upper_val = mean_val + 1.96 * std
        
        # Round to 2 decimal places
        mean_val = round(mean_val, 2)
        lower_val = round(lower_val, 2)
        upper_val = round(upper_val, 2)
        
        return mean_val, lower_val, upper_val
        
    except Exception as e:
        logger.error(f"Error in adaptive forecast: {e}\n{traceback.format_exc()}")
        # Return the last value with a default confidence interval
        if len(time_series) > 0:
            mean_val = float(time_series[-1])
        else:
            mean_val = 0.0
        
        std = mean_val * 0.01  # 1% of mean
        lower_val = mean_val - 1.96 * std
        upper_val = mean_val + 1.96 * std
        
        return mean_val, lower_val, upper_val

def ensemble_forecast(time_series: np.ndarray, 
                     timestamp: Optional[datetime] = None,
                     forecast_horizon: int = 1) -> Dict[str, Any]:
    """
    Generate ensemble forecast using multiple methods and combine them.
    
    :param time_series: historical time series data as numpy array
    :param timestamp: optional timestamp for the forecast
    :param forecast_horizon: number of steps to forecast ahead
    
    :return: dictionary with forecast results and metadata
    """
    try:
        if len(time_series) < 10:
            logger.warning(f"Time series too short ({len(time_series)} points) for ensemble forecast")
            # Fall back to simple forecast
            mean, lower, upper = adaptive_forecast(time_series, forecast_horizon)
            return {
                'forecast': mean,
                'lower_bound': lower,
                'upper_bound': upper,
                'std': (upper - lower) / 3.92,  # Convert 95% CI to std
                'methods_used': ['simple'],
                'timestamp': timestamp
            }
        
        # List to store predictions from different methods
        predictions = []
        
        # 1. Moving average with exponential weighting
        try:
            # Use the last 10 points with exponential weights
            window_size = min(len(time_series), 10)
            weights = np.exp(np.linspace(0, 1, window_size))
            weights = weights / weights.sum()
            ma_pred = np.average(time_series[-window_size:], weights=weights)
            predictions.append((ma_pred, 0.3, "ExpMovingAvg"))
        except Exception as e:
            logger.warning(f"Error in moving average calculation: {e}")
        
        # 2. Linear trend prediction
        try:
            # Create a simple time index
            indices = np.arange(len(time_series[-30:]))
            values = time_series[-30:]
            
            # Fit a linear model
            from scipy import stats
            slope, intercept, r_value, p_value, std_err = stats.linregress(indices, values)
            
            # Predict the next value
            next_idx = len(indices)
            trend_pred = slope * next_idx + intercept
            
            # Weight based on how good the linear fit is (r-squared)
            trend_weight = min(0.3, r_value**2)  # Cap at 0.3
            
            if not np.isnan(trend_pred):
                predictions.append((trend_pred, trend_weight, "LinearTrend"))
        except Exception as e:
            logger.warning(f"Error in linear trend calculation: {e}")
        
        # 3. ARIMA prediction if statsmodels is available
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            # Use a simple ARIMA model
            arima_model = ARIMA(time_series[-60:], order=(1,0,0))
            arima_result = arima_model.fit()
            
            # Forecast one step ahead
            arima_pred = arima_result.forecast(steps=forecast_horizon)[0]
            
            # Fixed weight for ARIMA
            arima_weight = 0.3
            
            if not np.isnan(arima_pred):
                predictions.append((arima_pred, arima_weight, "ARIMA"))
        except (ImportError, Exception) as e:
            logger.debug(f"ARIMA prediction not available: {e}")
        
        # 4. Last value (persistence model)
        last_value = time_series[-1]
        predictions.append((last_value, 0.1, "Persistence"))
        
        # Combine predictions with weights
        if predictions:
            # Normalize weights
            total_weight = sum(w for _, w, _ in predictions)
            if total_weight > 0:
                normalized_predictions = [(p, w/total_weight, m) for p, w, m in predictions]
                
                # Calculate weighted average
                ensemble_pred = sum(p * w for p, w, _ in normalized_predictions)
            else:
                # If weights sum to zero, use the last value
                ensemble_pred = last_value
                
            # Calculate standard deviation for confidence interval
            if len(time_series) >= 5:
                std = np.std(time_series[-5:])
            else:
                std = last_value * 0.005  # 0.5% of last value
                
            # Calculate confidence intervals (95%)
            lower_bound = ensemble_pred - 1.96 * std
            upper_bound = ensemble_pred + 1.96 * std
            
            # Round to 2 decimal places
            ensemble_pred = round(ensemble_pred, 2)
            lower_bound = round(lower_bound, 2)
            upper_bound = round(upper_bound, 2)
            
            # Create result dictionary
            result = {
                'forecast': ensemble_pred,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'std': std,
                'methods_used': [m for _, _, m in predictions],
                'method_weights': {m: round(w, 2) for _, w, m in normalized_predictions},
                'timestamp': timestamp
            }
            
            return result
        else:
            # Fall back to simple forecast
            mean, lower, upper = adaptive_forecast(time_series, forecast_horizon)
            return {
                'forecast': mean,
                'lower_bound': lower,
                'upper_bound': upper,
                'std': (upper - lower) / 3.92,  # Convert 95% CI to std
                'methods_used': ['fallback'],
                'timestamp': timestamp
            }
    except Exception as e:
        logger.error(f"Error in ensemble forecast: {e}\n{traceback.format_exc()}")
        # Return a simple forecast as fallback
        if len(time_series) > 0:
            mean_val = float(time_series[-1])
        else:
            mean_val = 0.0
            
        std = mean_val * 0.01  # 1% of mean
        lower_val = mean_val - 1.96 * std
        upper_val = mean_val + 1.96 * std
        
        return {
            'forecast': round(mean_val, 2),
            'lower_bound': round(lower_val, 2),
            'upper_bound': round(upper_val, 2),
            'std': std,
            'methods_used': ['emergency_fallback'],
            'timestamp': timestamp
        }

def detect_price_anomalies(price_series: np.ndarray, 
                          window_size: int = 20, 
                          z_threshold: float = 3.0) -> List[int]:
    """
    Detect anomalies in price data using z-score method.
    
    :param price_series: array of price values
    :param window_size: size of rolling window for z-score calculation
    :param z_threshold: z-score threshold for anomaly detection
    
    :return: list of indices where anomalies were detected
    """
    try:
        if len(price_series) < window_size + 1:
            logger.warning(f"Price series too short ({len(price_series)}) for anomaly detection with window size {window_size}")
            return []
            
        # Convert to numpy array if needed
        if not isinstance(price_series, np.ndarray):
            price_series = np.array(price_series)
            
        # Calculate rolling mean and std
        anomaly_indices = []
        
        for i in range(window_size, len(price_series)):
            # Get the window
            window = price_series[i-window_size:i]
            
            # Calculate mean and std of the window
            window_mean = np.mean(window)
            window_std = np.std(window)
            
            # Skip if std is zero
            if window_std == 0:
                continue
                
            # Calculate z-score
            z_score = abs((price_series[i] - window_mean) / window_std)
            
            # Check if it's an anomaly
            if z_score > z_threshold:
                anomaly_indices.append(i)
                
        return anomaly_indices
    except Exception as e:
        logger.error(f"Error detecting price anomalies: {e}\n{traceback.format_exc()}")
        return []

def preprocess_price_series(price_series: np.ndarray, 
                           remove_anomalies: bool = True,
                           interpolate_missing: bool = True,
                           z_threshold: float = 3.0) -> np.ndarray:
    """
    Preprocess price time series data for forecasting.
    
    :param price_series: array of price values
    :param remove_anomalies: whether to remove and replace anomalies
    :param interpolate_missing: whether to interpolate missing values
    :param z_threshold: z-score threshold for anomaly detection
    
    :return: preprocessed price series
    """
    try:
        # Convert to numpy array if needed
        if not isinstance(price_series, np.ndarray):
            price_series = np.array(price_series)
            
        # Handle missing values (NaN)
        if interpolate_missing and np.isnan(price_series).any():
            # Get indices of non-NaN values
            valid_indices = np.where(~np.isnan(price_series))[0]
            
            if len(valid_indices) < 2:
                # Not enough valid points for interpolation
                logger.warning("Not enough valid points for interpolation")
                return price_series
                
            # Get valid values
            valid_values = price_series[valid_indices]
            
            # Create interpolation function
            from scipy import interpolate
            f = interpolate.interp1d(valid_indices, valid_values, 
                                     bounds_error=False, 
                                     fill_value=(valid_values[0], valid_values[-1]))
                                     
            # Create index array for all points
            all_indices = np.arange(len(price_series))
            
            # Interpolate
            price_series = f(all_indices)
            
        # Remove anomalies
        if remove_anomalies and len(price_series) > 10:
            # Detect anomalies
            anomaly_indices = detect_price_anomalies(price_series, z_threshold=z_threshold)
            
            # Replace anomalies with local median
            for idx in anomaly_indices:
                # Use local median (5 points before and after if available)
                start_idx = max(0, idx - 5)
                end_idx = min(len(price_series), idx + 6)
                
                # Get local values excluding the anomaly itself
                local_values = np.concatenate([
                    price_series[start_idx:idx],
                    price_series[idx+1:end_idx]
                ])
                
                if len(local_values) > 0:
                    # Replace with median
                    price_series[idx] = np.median(local_values)
                    
        return price_series
    except Exception as e:
        logger.error(f"Error preprocessing price series: {e}\n{traceback.format_exc()}")
        return price_series


