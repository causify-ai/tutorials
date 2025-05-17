#!/usr/bin/env python3
"""
Bitcoin price dashboard using Streamlit.
Displays real-time price data and predictions.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import logging
import traceback
from utilities.timestamp_format import parse_timestamp, format_timestamp
from utilities.price_format import usd_to_display_str
from utilities.unified_config import get_service_config
import numpy as np
import sys
import json

# Try to import scipy.stats, but handle if not available
try:
    import scipy.stats as stats
except ImportError:
    # Define a minimal stats module for basic functionality
    class MinimalStats:
        def norm(self):
            class NormalDist:
                def pdf(self, x, loc, scale):
                    # Simple normal distribution approximation
                    return np.exp(-((x - loc) ** 2) / (2 * scale ** 2)) / (scale * np.sqrt(2 * np.pi))
            return NormalDist()
            
        def zscore(self, a):
            # Calculate z-scores (standardized values)
            mean = np.mean(a)
            std = np.std(a)
            if std == 0:
                return np.zeros_like(a)
            return (a - mean) / std
    
    stats = MinimalStats()

# Get service name from environment or use default
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'dashboard')

# Load config using unified config parser
config = get_service_config(SERVICE_NAME)

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(config['app']['log_level']),
    format=config['app']['log_format'],
    datefmt=config['app']['log_date_format']
)
logger = logging.getLogger(__name__)
logger.info(f"Starting {SERVICE_NAME} service with unified configuration")

# Set page config
st.set_page_config(
    page_title="Bitcoin Price Forecasting Dashboard",
    page_icon="📈",
    layout="wide"
)

# Constants
REFRESH_INTERVAL = 1  # 1 second to match web app
PRICE_FILE = config['data']['raw_data']['instant_data']['file']
PREDICTIONS_FILE = config['data']['predictions']['instant_data']['predictions_file']
METRICS_FILE = config['data']['predictions']['instant_data']['metrics_file']

# Set consistent time window for all charts (60 minutes)
TIME_WINDOW_MINUTES = 30

# Update config to ensure consistency
if 'plot_settings' not in config['dashboard']:
    config['dashboard']['plot_settings'] = {}
config['dashboard']['plot_settings']['time_window_minutes'] = TIME_WINDOW_MINUTES
config['dashboard']['refresh_interval'] = REFRESH_INTERVAL  # Ensure config is updated with new refresh interval

# Add a cold start handling configuration
if 'cold_start' not in config['dashboard']:
    config['dashboard']['cold_start'] = {
        'enabled': True,
        'min_data_points': 10  # Minimum number of data points to consider valid for visualizing
    }

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import utility functions
from utilities.config_parser import load_config

def load_csv_safely(file_path, columns, skip_rows=1):
    """Safely load CSV data with error handling"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return pd.DataFrame(columns=columns)
            
        df = pd.read_csv(
            file_path,
            names=columns,
            skiprows=skip_rows,
            on_bad_lines='warn'  # Skip bad lines but warn
        )
        
        # Ensure all required columns are present
        for col in columns:
            if col not in df.columns:
                logger.warning(f"Missing column {col} in {file_path}")
                df[col] = None
                
        # Handle timestamp conversion separately with error handling
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
            
        return df
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}\n{traceback.format_exc()}")
        return pd.DataFrame(columns=columns)

@st.cache_data(ttl=config['dashboard']['refresh_interval'])
def load_data():
    """Load the latest data with caching."""
    try:
        # Load price data
        if not os.path.exists(PRICE_FILE):
            logger.warning(f"Price file not found: {PRICE_FILE}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
        price_df = pd.read_csv(
            PRICE_FILE,
            names=config['data_format']['columns']['raw_data']['names'],
            skiprows=1,
            parse_dates=['timestamp']
        )
        
        # Load predictions if available
        if os.path.exists(PREDICTIONS_FILE):
            pred_df = pd.read_csv(
                PREDICTIONS_FILE,
                parse_dates=['timestamp'] 
            )
        else:
            pred_df = pd.DataFrame()
            
        # Load metrics if available
        if os.path.exists(METRICS_FILE):
            # Get expected column names from config
            expected_metrics_columns = config['data_format']['columns']['metrics']['names']
            
            try:
                # First attempt to load with all expected columns
                metrics_df = pd.read_csv(
                    METRICS_FILE,
                    parse_dates=['timestamp']
                )
                
                # If actual_error column doesn't exist in old files, add it with NaN values
                if 'actual_error' not in metrics_df.columns and 'actual_error' in expected_metrics_columns:
                    metrics_df['actual_error'] = np.nan
                    logger.info("Added missing actual_error column to loaded metrics data")
                
            except Exception as e:
                logger.warning(f"Error loading metrics with full columns: {e}, trying with usecols")
                # Fall back to using only columns that exist in the file
                metrics_df = pd.read_csv(
                    METRICS_FILE,
                    parse_dates=['timestamp'],
                    usecols=lambda col: col in expected_metrics_columns
                )
                
                # Add missing columns with NaN values
                for col in expected_metrics_columns:
                    if col not in metrics_df.columns:
                        metrics_df[col] = np.nan
                        logger.info(f"Added missing column {col} to loaded metrics data")
        else:
            metrics_df = pd.DataFrame()
        
        logger.info(f"Loaded data: price={len(price_df)} rows, pred={len(pred_df)} rows, metrics={len(metrics_df)} rows")
        return price_df, pred_df, metrics_df
        
    except Exception as e:
        logger.error(f"Error loading data: {e}\n{traceback.format_exc()}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def align_metrics_with_data(metrics_df, price_df, pred_df):
    """
    Ensure metrics only include timestamps where we have both actual and predicted data.
    This maintains data veracity by only showing metrics for timestamps with complete data.
    """
    try:
        if metrics_df.empty or price_df.empty or pred_df.empty:
            logger.info(f"Empty dataframes: metrics={metrics_df.empty}, price={price_df.empty}, pred={pred_df.empty}")
            return metrics_df
            
        # Log data info before alignment
        logger.info(f"Before alignment: metrics={len(metrics_df)} rows, price={len(price_df)} rows, pred={len(pred_df)} rows")
        
        # Log sample timestamps from each dataframe
        if not metrics_df.empty:
            logger.info(f"Sample metrics timestamps: {metrics_df['timestamp'].iloc[0]} to {metrics_df['timestamp'].iloc[-1]}")
        if not price_df.empty:
            logger.info(f"Sample price timestamps: {price_df['timestamp'].iloc[0]} to {price_df['timestamp'].iloc[-1]}")
        if not pred_df.empty:
            logger.info(f"Sample pred timestamps: {pred_df['timestamp'].iloc[0]} to {pred_df['timestamp'].iloc[-1]}")
            
        # Round timestamps to the nearest second for comparison (accounting for tiny timestamp differences)
        metrics_df = metrics_df.copy()
        price_df = price_df.copy()
        pred_df = pred_df.copy()
        
        # Ensure timestamp columns are datetime type
        metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
        price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
        pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'])
        
        # Round to seconds to handle microsecond differences
        metrics_df['timestamp_rounded'] = metrics_df['timestamp'].dt.floor('S')
        price_df['timestamp_rounded'] = price_df['timestamp'].dt.floor('S')
        pred_df['timestamp_rounded'] = pred_df['timestamp'].dt.floor('S')
        
        # Create sets of timestamps
        price_timestamps = set(price_df['timestamp_rounded'])
        pred_timestamps = set(pred_df['timestamp_rounded'])
        
        # Find timestamps that exist in both price and prediction data
        valid_timestamps = price_timestamps.intersection(pred_timestamps)
        logger.info(f"Found {len(valid_timestamps)} timestamps in both price and prediction data")
        
        # Filter metrics dataframe to only include timestamps with both actual and predicted data
        metrics_df = metrics_df[metrics_df['timestamp_rounded'].isin(valid_timestamps)]
        
        # Drop the temporary rounded timestamp column
        metrics_df = metrics_df.drop('timestamp_rounded', axis=1)
        
        logger.info(f"Aligned metrics data: {len(metrics_df)} valid entries with matching timestamps")
        
        # If we have any valid entries, log a sample
        if not metrics_df.empty:
            logger.info(f"Sample aligned metrics: {metrics_df.iloc[0].to_dict()}")
            
        return metrics_df
        
    except Exception as e:
        logger.error(f"Error aligning metrics with data: {e}\n{traceback.format_exc()}")
        return metrics_df  # Return original dataframe in case of error

def filter_last_n_minutes(df, n_minutes, check_time=True):
    """Filter DataFrame to only include data from the last n minutes or simply return the last n_minutes of data."""
    if df is None or df.empty:
        return df
    
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Ensure timestamp column exists and has datetime values
    if 'timestamp' not in df.columns:
        logger.warning("No timestamp column found for filtering")
        return df
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # If check_time=True, filter by actual time, otherwise just return latest data
    if check_time:
        # Get current time and calculate cutoff
        now = pd.Timestamp.now(tz=None)
        cutoff = now - pd.Timedelta(minutes=n_minutes)
        # Filter data by time
        filtered_df = df[df['timestamp'] >= cutoff]
        
        # If no data matches the time filter, just return the latest entries
        if filtered_df.empty:
            logger.warning("No data within time window, using latest entries instead")
            # Take the last n entries as a fallback
            n_entries = min(30, len(df))
            filtered_df = df.tail(n_entries)
    else:
        # Just take the most recent entries (useful for historical data)
        n_entries = min(30, len(df))
        filtered_df = df.tail(n_entries)
    
    return filtered_df

def create_price_chart(price_df):
    """Create candlestick chart for actual price."""
    fig = go.Figure()
    
    if price_df is not None and not price_df.empty:
        # Ensure we have the required columns
        required_cols = ['timestamp', 'open', 'high', 'low', 'close']
        if all(col in price_df.columns for col in required_cols):
            # Create candlestick chart
            fig.add_trace(go.Candlestick(
                x=price_df['timestamp'],
                open=price_df['open'],
                high=price_df['high'],
                low=price_df['low'],
                close=price_df['close'],
                name='Bitcoin Price',
                increasing_line_color=config['dashboard']['colors']['actual_up'],
                decreasing_line_color=config['dashboard']['colors']['actual_down']
            ))
        else:
            missing = [col for col in required_cols if col not in price_df.columns]
            logger.warning(f"Missing columns for candlestick chart: {missing}")
    
    # Update layout
    fig.update_layout(
        title='Bitcoin Price (Candlestick Chart)',
        yaxis_title='Price (USD)',
        xaxis_title='Time',
        template='plotly_white',
        height=config['dashboard']['chart_height'],
        showlegend=False,
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            title='Time',
            tickformat='%H:%M',  # Simplified format showing only hours and minutes
            nticks=10,
            tickangle=-45,
            showgrid=True,
            fixedrange=True  # Prevent zooming on x-axis for consistent view
        ),
        yaxis=dict(
            fixedrange=False  # Allow zooming on y-axis
        ),
        margin=dict(l=60, r=40, t=50, b=80)  # Add more margin space for labels
    )
    
    # Dynamic x-axis range based on available data for cold start handling
    if price_df is not None and not price_df.empty:
        # Get the timestamp range
        max_time = price_df['timestamp'].max()
        
        # Check if we're in a cold start scenario (less than the full time window)
        time_span_minutes = (price_df['timestamp'].max() - price_df['timestamp'].min()).total_seconds() / 60
        data_points = len(price_df)
        
        # Cold start handling: For less than TIME_WINDOW_MINUTES of data, use all available data
        if config['dashboard']['cold_start']['enabled'] and time_span_minutes < TIME_WINDOW_MINUTES and data_points >= config['dashboard']['cold_start']['min_data_points']:
            # Use the actual data range with a small padding
            min_time = price_df['timestamp'].min()
            padding = pd.Timedelta(seconds=30)  # Add 30 seconds padding
            fig.update_xaxes(range=[min_time - padding, max_time + padding])
            logger.info(f"Cold start mode: Using {time_span_minutes:.1f} minutes of data instead of {TIME_WINDOW_MINUTES}")
        else:
            # Standard mode: Use the full TIME_WINDOW_MINUTES range
            min_time = max_time - pd.Timedelta(minutes=TIME_WINDOW_MINUTES)
            fig.update_xaxes(range=[min_time, max_time])
    
    return fig

def create_prediction_chart(price_df, pred_df):
    """Create prediction comparison chart with confidence interval."""
    fig = go.Figure()
    
    # Check if we have data to plot
    has_price_data = price_df is not None and not price_df.empty and 'close' in price_df.columns
    has_pred_data = pred_df is not None and not pred_df.empty
    
    # Log data for debugging
    if has_price_data:
        logger.info(f"Price data time range: {price_df['timestamp'].min()} to {price_df['timestamp'].max()}")
    if has_pred_data:
        logger.info(f"Prediction data time range: {pred_df['timestamp'].min()} to {pred_df['timestamp'].max()}")
    
    # Determine if we need dual-axis presentation
    use_secondary_y = False
    if has_price_data and has_pred_data:
        # Get time ranges to compare
        price_min = price_df['timestamp'].min()
        price_max = price_df['timestamp'].max()
        pred_min = pred_df['timestamp'].min()
        pred_max = pred_df['timestamp'].max()
        
        # Check if the timestamp ranges overlap (with a 1-day buffer)
        one_day = pd.Timedelta(days=1)
        ranges_overlap = (pred_min - one_day <= price_max and pred_max + one_day >= price_min)
        
        if not ranges_overlap:
            use_secondary_y = True
            logger.info("Using secondary y-axis for predictions due to non-overlapping timestamps")
    
    # Add actual price line if data exists
    if has_price_data:
        fig.add_trace(go.Scatter(
            x=price_df['timestamp'],
            y=price_df['close'],
            name='Actual Price',
            line=dict(color=config['dashboard']['colors']['actual'], width=2)
        ))
    
    # Add prediction line and confidence interval if data exists
    if has_pred_data:
        required_cols = ['timestamp', 'pred_price', 'pred_lower', 'pred_upper']
        if all(col in pred_df.columns for col in required_cols):
            # Determine if we should use a time-label for the prediction based on date differences
            if has_price_data:
                # Make sure we're comparing dates, not timestamps
                latest_price_date = price_df['timestamp'].iloc[-1].date()
                latest_pred_date = pred_df['timestamp'].iloc[-1].date()
                
                # Add date to label if dates are different
                time_label = ""
                if latest_price_date != latest_pred_date:
                    # Format the date in ISO8601 format for consistency
                    date_str = format_timestamp(latest_pred_date, use_t_separator=True).split('T')[0]
                    time_label = f" ({date_str})"
                    
                prediction_name = f"Predicted Price{time_label}"
                upper_bound_name = f"Upper Bound{time_label}"
                lower_bound_name = f"Lower Bound{time_label}"
            else:
                prediction_name = "Predicted Price"
                upper_bound_name = "Upper Bound"
                lower_bound_name = "Lower Bound"
            
            # Add prediction trace
            fig.add_trace(go.Scatter(
                x=pred_df['timestamp'],
                y=pred_df['pred_price'],
                name=prediction_name,
                line=dict(color=config['dashboard']['colors']['predicted'], width=2),
                yaxis="y2" if use_secondary_y else "y"
            ))
            
            # Add upper bound
            fig.add_trace(go.Scatter(
                x=pred_df['timestamp'],
                y=pred_df['pred_upper'],
                name=upper_bound_name,
                line=dict(color=config['dashboard']['colors']['confidence'], dash='dash'),
                showlegend=True,
                yaxis="y2" if use_secondary_y else "y"
            ))
            
            # Add lower bound with fill
            fig.add_trace(go.Scatter(
                x=pred_df['timestamp'],
                y=pred_df['pred_lower'],
                name=lower_bound_name,
                fill='tonexty',
                line=dict(color=config['dashboard']['colors']['confidence'], dash='dash'),
                showlegend=True,
                yaxis="y2" if use_secondary_y else "y"
            ))
            
            # Configure the secondary y-axis if needed
            if use_secondary_y:
                fig.update_layout(
                    yaxis2=dict(
                        title="Predicted Price (USD)",
                        side="right",
                        overlaying="y",
                        tickformat=",.0f",
                        tickprefix="$",
                    )
                )
    
    # Compute y-axis range with margin for the primary axis
    all_y = []
    if has_price_data:
        all_y.extend(price_df['close'].dropna().values)
    
    # Set primary y-axis range if we have price data
    if all_y:
        y_min, y_max = min(all_y), max(all_y)
        margin = (y_max - y_min) * 0.02 if y_max > y_min else 1
        y_range = [y_min - margin, y_max + margin]
    else:
        y_range = None
    
    # Create appropriate title based on the data being shown
    if has_price_data and has_pred_data:
        if use_secondary_y:
            title = 'Actual Price and Predicted Price (Different Time Periods)'
        else:
            title = 'Predicted Price with Confidence Interval vs Actual'
    elif has_price_data:
        title = 'Actual Bitcoin Price'
    elif has_pred_data:
        title = 'Bitcoin Price Predictions'
    else:
        title = 'No Price Data Available'
    
    # Update layout
    fig.update_layout(
        title=title,
        yaxis_title='Price (USD)',
        xaxis_title='Time',
        template='plotly_white',
        height=config['dashboard']['chart_height'],
        showlegend=True,
        xaxis=dict(
            title='Time',
            tickformat='%H:%M',  # Simplified format showing only hours and minutes
            nticks=10,
            tickangle=-45,
            showgrid=True,
            fixedrange=True  # Prevent zooming on x-axis for consistent view
        ),
        yaxis=dict(
            title='Price (USD)',
            tickformat=',.0f',
            tickprefix='$',
            fixedrange=False  # Allow zooming on y-axis
        ),
        margin=dict(l=60, r=40, t=50, b=80)  # Add more margin space for labels
    )
    
    # Set x-axis range for consistent time window
    if has_price_data:
        max_time = price_df['timestamp'].max()
        min_time = max_time - pd.Timedelta(minutes=TIME_WINDOW_MINUTES)
        fig.update_xaxes(range=[min_time, max_time])
    elif has_pred_data:
        max_time = pred_df['timestamp'].max()
        min_time = max_time - pd.Timedelta(minutes=TIME_WINDOW_MINUTES)
        fig.update_xaxes(range=[min_time, max_time])
    
    return fig

def create_mae_chart(metrics_df):
    """Create error chart showing actual error at each timestamp alongside MAE."""
    fig = go.Figure()
    
    if metrics_df is not None and not metrics_df.empty:
        has_mae = 'mae' in metrics_df.columns
        has_actual_error = 'actual_error' in metrics_df.columns
        
        # Log metrics data for debugging
        logger.info(f"Adding error data to chart: {len(metrics_df)} rows")
        if not metrics_df.empty:
            debug_cols = ['timestamp']
            if has_mae:
                debug_cols.append('mae')
            if has_actual_error:
                debug_cols.append('actual_error')
            logger.info(f"Sample metrics: {metrics_df.iloc[0][debug_cols].to_dict()}")
        
        # Filter out potentially corrupted data
        filtered_df = metrics_df.copy()
        
        if has_actual_error:
            # Make sure actual_error is numeric
            filtered_df['actual_error'] = pd.to_numeric(filtered_df['actual_error'], errors='coerce')
            
            # Filter out NaN values
            filtered_df = filtered_df.dropna(subset=['actual_error'])
            
            # Add actual error line (positive values are when actual > predicted, negative when predicted > actual)
            fig.add_trace(go.Scatter(
                x=filtered_df['timestamp'],
                y=filtered_df['actual_error'],
                name='Actual Error',
                line=dict(color='#3498db', width=2),  # Blue color to match web app
                hovertemplate='%{y:,.2f}'
            ))
            
            # Add zero line to show the baseline (perfect prediction)
            fig.add_trace(go.Scatter(
                x=[filtered_df['timestamp'].min(), filtered_df['timestamp'].max()],
                y=[0, 0],
                name='Perfect Prediction',
                line=dict(color='gray', width=1, dash='dash')
            ))
            
            # Calculate average error (arithmetic mean of all errors, including sign)
            avg_error = filtered_df['actual_error'].mean()
            
            # Calculate MAE (Mean Absolute Error - arithmetic mean of absolute errors)
            abs_errors = filtered_df['actual_error'].abs()
            mae = abs_errors.mean()
            
            # Round to 2 decimal places for display consistency with web app
            avg_error = round(avg_error, 2)
            mae = round(mae, 2)
            
            # Log the error calculations for comparison with web app
            logger.info(f"Error statistics - Avg Error: {avg_error:.2f}, MAE: {mae:.2f}")
            
            # Add a horizontal line for the average error
            fig.add_trace(go.Scatter(
                x=[filtered_df['timestamp'].min(), filtered_df['timestamp'].max()],
                y=[avg_error, avg_error],
                name=f'Avg Error: {avg_error:.2f}',
                line=dict(color='blue', width=1, dash='dash'),
                visible=True  # Ensure the line is visible
            ))
            
            # Add MAE as a horizontal line
            fig.add_trace(go.Scatter(
                x=[filtered_df['timestamp'].min(), filtered_df['timestamp'].max()],
                y=[mae, mae],
                name=f'MAE: {mae:.2f}',
                line=dict(color='#e74c3c', width=2, dash='dot'),  # Red color to match web app
                opacity=0.7,
                hovertemplate='%{y:,.2f}',
                visible=True  # Ensure the line is visible
            ))
        else:
            # If no actual_error column, use the mae column if available
            # This is a fallback for backward compatibility
            filtered_df['mae'] = pd.to_numeric(filtered_df['mae'], errors='coerce')
            filtered_df = filtered_df.dropna(subset=['mae'])
            
            # Calculate the average of the mae column
            mean_mae = filtered_df['mae'].mean()
            mean_mae = round(mean_mae, 2)  # Round to 2 decimal places for consistency
            
            # Add MAE as a horizontal line
            fig.add_trace(go.Scatter(
                x=[filtered_df['timestamp'].min(), filtered_df['timestamp'].max()],
                y=[mean_mae, mean_mae],
                name=f'MAE: {mean_mae:.2f}',
                line=dict(color='#e74c3c', width=2, dash='dot'),  # Red color to match web app
                opacity=0.7,
                hovertemplate='%{y:,.2f}',
                visible=True  # Ensure the line is visible
            ))
    
    fig.update_layout(
        title='Prediction Error Over Time',
        yaxis_title='Error (USD)',
        xaxis_title='Time',
        template='plotly_white',
        height=int(config['dashboard']['chart_height'] * 0.7),
        showlegend=True,
        yaxis=dict(
            tickformat=',.2f',  # Show 2 decimal places for better precision
            tickprefix='$',
            ticksuffix='',
            tickmode='auto',
            fixedrange=False  # Allow zooming on y-axis
        ),
        xaxis=dict(
            title='Time',
            tickformat='%H:%M',  # Simplified format showing only hours and minutes
            nticks=10,
            tickangle=-45,
            showgrid=True,
            fixedrange=True  # Prevent zooming on x-axis for consistent view
        ),
        margin=dict(l=60, r=40, t=50, b=80)  # Add more margin space for labels
    )
    
    # Force x-axis range to show full 30 minutes if we have data
    if metrics_df is not None and not metrics_df.empty:
        # Get the timestamp range
        max_time = metrics_df['timestamp'].max()
        
        # Standard mode: Use the full TIME_WINDOW_MINUTES range
        min_time = max_time - pd.Timedelta(minutes=TIME_WINDOW_MINUTES)
        fig.update_xaxes(range=[min_time, max_time])
    
    return fig

def create_error_distribution_chart(metrics_df):
    """Create a histogram showing the distribution of prediction errors."""
    fig = go.Figure()
    
    if metrics_df is not None and not metrics_df.empty and 'actual_error' in metrics_df.columns:
        # Make sure actual_error is numeric
        metrics_df['actual_error'] = pd.to_numeric(metrics_df['actual_error'], errors='coerce')
        
        # Filter out NaN values
        filtered_df = metrics_df.dropna(subset=['actual_error'])
        
        if not filtered_df.empty:
            # Calculate statistics
            mean_error = filtered_df['actual_error'].mean()
            median_error = filtered_df['actual_error'].median()
            std_error = filtered_df['actual_error'].std()
            
            # Round to 2 decimal places for consistency with web app
            mean_error = round(mean_error, 2)
            median_error = round(median_error, 2)
            std_error = round(std_error, 2)
            
            # Log the statistics for comparison with web app
            logger.info(f"Error distribution statistics - Mean: {mean_error:.2f}, Median: {median_error:.2f}, StdDev: {std_error:.2f}")
            
            # Create histogram of errors with consistent binning (20 bins)
            fig.add_trace(go.Histogram(
                x=filtered_df['actual_error'],
                nbinsx=20,
                name='Error Distribution',
                marker_color='lightblue',
                opacity=0.8
            ))
            
            # Add mean line
            fig.add_vline(
                x=mean_error,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {mean_error:.2f}",
                annotation_position="top right"
            )
            
            # Add median line
            fig.add_vline(
                x=median_error,
                line_dash="dash",
                line_color="green",
                annotation_text=f"Median: {median_error:.2f}",
                annotation_position="top left"
            )
            
            # Add perfect prediction line (zero error)
            fig.add_vline(
                x=0,
                line_dash="solid",
                line_color="black",
                annotation_text="Perfect",
                annotation_position="bottom"
            )
            
            # Try to add normal distribution curve if scipy is available
            try:
                # Generate x values for the curve
                x_range = np.linspace(
                    filtered_df['actual_error'].min(),
                    filtered_df['actual_error'].max(),
                    100
                )
                
                # Get the normal distribution curve
                if hasattr(stats, 'norm') and callable(getattr(stats.norm, 'pdf', None)):
                    # Use scipy.stats if available
                    y_norm = stats.norm.pdf(x_range, mean_error, std_error)
                else:
                    # Use our minimal implementation
                    y_norm = stats.norm().pdf(x_range, mean_error, std_error)
                
                # Create a histogram to get the bin heights for proper scaling
                hist_values, bin_edges = np.histogram(filtered_df['actual_error'], bins=20)
                max_bin_height = max(hist_values)
                
                # Find the maximum value in the normal PDF
                max_pdf_value = max(y_norm) if len(y_norm) > 0 else 1
                
                # Scale factor to match histogram height
                scale_factor = max_bin_height / max_pdf_value if max_pdf_value > 0 else 1
                
                # Apply scaling
                y_scaled = y_norm * scale_factor
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_scaled,
                    mode='lines',
                    name='Normal Distribution',
                    line=dict(color='darkblue', width=2)
                ))
            except Exception as e:
                # Log the error but continue without the normal curve
                logger.warning(f"Could not add normal distribution curve: {e}")
    
    fig.update_layout(
        title='Prediction Error Distribution',
        xaxis_title='Error (USD)',
        yaxis_title='Frequency',
        template='plotly_white',
        height=int(config['dashboard']['chart_height'] * 0.5),
        showlegend=True,
        xaxis=dict(
            tickformat=',.2f',  # Show 2 decimal places for better precision
            tickprefix='$',
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2
        ),
        margin=dict(l=60, r=40, t=50, b=80)  # Add more margin space for labels
    )
    
    return fig

def get_last_update_time(price_df, pred_df):
    """Get the most recent timestamp from either price or prediction data"""
    last_update = None
    
    if price_df is not None and not price_df.empty:
        price_time = price_df['timestamp'].max()
        last_update = price_time
    
    if pred_df is not None and not pred_df.empty:
        pred_time = pred_df['timestamp'].max()
        if last_update is None or pred_time > last_update:
            last_update = pred_time
    
    if last_update is not None:
        return format_timestamp(last_update, use_t_separator=True)
    else:
        return "No data available"

def check_cold_start(price_df):
    """Check if we're in a cold start scenario (less than the full time window)"""
    is_cold_start = False
    cold_start_minutes = 0
    
    if price_df is not None and not price_df.empty and len(price_df) >= config['dashboard']['cold_start']['min_data_points']:
        # Calculate time span
        time_span = price_df['timestamp'].max() - price_df['timestamp'].min()
        cold_start_minutes = time_span.total_seconds() / 60
        
        # If less than the full time window, we're in cold start
        if cold_start_minutes < TIME_WINDOW_MINUTES:
            is_cold_start = True
    
    return is_cold_start, cold_start_minutes

def get_current_price(price_df):
    """Get the most recent price"""
    if price_df is not None and not price_df.empty:
        return price_df['close'].iloc[-1]
    return None

def get_price_change(price_df):
    """Calculate price change over the available time period"""
    if price_df is not None and not price_df.empty and len(price_df) > 1:
        latest_price = price_df['close'].iloc[-1]
        first_price = price_df['close'].iloc[0]
        price_change = latest_price - first_price
        price_change_pct = (price_change / first_price) * 100
        return price_change, price_change_pct
    return None, None

def get_prediction_error_metrics(metrics_df):
    """Calculate prediction error metrics"""
    if metrics_df is not None and not metrics_df.empty and 'actual_error' in metrics_df.columns:
        # Make sure actual_error is numeric
        metrics_df['actual_error'] = pd.to_numeric(metrics_df['actual_error'], errors='coerce')
        
        # Filter out NaN values
        filtered_df = metrics_df.dropna(subset=['actual_error'])
        
        if not filtered_df.empty:
            # Calculate average error (arithmetic mean of all errors, including sign)
            avg_error = filtered_df['actual_error'].mean()
            
            # Calculate MAE (Mean Absolute Error - arithmetic mean of absolute errors)
            mae = filtered_df['actual_error'].abs().mean()
            
            return round(avg_error, 2), round(mae, 2)
    
    return None, None

def main():
    """Main function for the Streamlit dashboard."""
    try:
        # Set page config is already called at the beginning of the file
        # No need to call it again here
        
        # Add title and description
        st.title("Bitcoin Price Forecasting Dashboard")
        st.markdown(
            """
            This dashboard shows real-time Bitcoin price data and forecasts.
            """
        )
        
        # Load data
        price_df, pred_df, metrics_df = load_data()
        
        # Log raw data info
        logger.info(f"Raw data loaded - price: {len(price_df)} rows, predictions: {len(pred_df)} rows, metrics: {len(metrics_df)} rows")
        
        # Filter data to last 30 minutes
        filtered_price_df = filter_last_n_minutes(price_df, 30)
        filtered_pred_df = filter_last_n_minutes(pred_df, 30)
        filtered_metrics_df = filter_last_n_minutes(metrics_df, 30)
        
        # Log filtered data info
        logger.info(f"After filtering - price: {len(filtered_price_df)} rows, predictions: {len(filtered_pred_df)} rows, metrics: {len(filtered_metrics_df)} rows")
        
        # Display last update time
        last_update = get_last_update_time(filtered_price_df, filtered_pred_df)
        if last_update:
            st.sidebar.markdown(f"**Last Update:** {last_update}")
        
        # Display cold start warning if needed
        is_cold_start, cold_start_minutes = check_cold_start(filtered_price_df)
        if is_cold_start:
            st.sidebar.warning(f"Cold Start Mode: Only {cold_start_minutes:.1f} minutes of data available")
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        # Current price
        current_price = get_current_price(filtered_price_df)
        if current_price:
            col1.metric(
                "Current Price (USD)",
                f"${current_price:.2f}"
            )
        else:
            col1.metric("Current Price (USD)", "Loading...")
        
        # Price change
        price_change, price_change_pct = get_price_change(filtered_price_df)
        if price_change is not None:
            col2.metric(
                "Price Change (30m)",
                f"${price_change:.2f}",
                f"{price_change_pct:.2f}%",
                delta_color="normal" if price_change >= 0 else "inverse"
            )
        else:
            col2.metric("Price Change (30m)", "Loading...")
        
        # Prediction error
        avg_error, mae = get_prediction_error_metrics(filtered_metrics_df)
        if mae is not None:
            col3.metric(
                "Prediction MAE",
                f"${mae:.2f}",
                f"Avg Error: ${avg_error:.2f}",
                delta_color="normal" if abs(avg_error) < mae else "inverse"
            )
        else:
            col3.metric("Prediction MAE", "Loading...")
        
        # Display charts
        st.plotly_chart(
            create_price_chart(filtered_price_df),
            use_container_width=True,
            key="price_chart"
        )
        
        st.plotly_chart(
            create_prediction_chart(filtered_price_df, filtered_pred_df),
            use_container_width=True,
            key="prediction_chart"
        )
        
        st.plotly_chart(
            create_mae_chart(filtered_metrics_df),
            use_container_width=True,
            key="mae_chart"
        )
        
        st.plotly_chart(
            create_error_distribution_chart(filtered_metrics_df),
            use_container_width=True,
            key="error_distribution_chart"
        )
        
        # Add footer with refresh info
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"Dashboard auto-refreshes every {REFRESH_INTERVAL} second(s)")
        
        # Auto-refresh using the current API with consistent interval
        time.sleep(REFRESH_INTERVAL)
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        logger.error(traceback.format_exc())
        st.error(f"An error occurred: {e}")
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main() 