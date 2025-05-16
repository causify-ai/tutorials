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
    page_title="Bitcoin Price Dashboard",
    page_icon="📈",
    layout="wide"
)

# Constants
REFRESH_INTERVAL = config['dashboard']['refresh_interval']
PRICE_FILE = config['data']['raw_data']['instant_data']['file']
PREDICTIONS_FILE = config['data']['predictions']['instant_data']['predictions_file']
METRICS_FILE = config['data']['predictions']['instant_data']['metrics_file']

# Set consistent time window for all charts (60 minutes)
TIME_WINDOW_MINUTES = 30

# Update config to ensure consistency
if 'plot_settings' not in config['dashboard']:
    config['dashboard']['plot_settings'] = {}
config['dashboard']['plot_settings']['time_window_minutes'] = TIME_WINDOW_MINUTES

# Add a cold start handling configuration
if 'cold_start' not in config['dashboard']:
    config['dashboard']['cold_start'] = {
        'enabled': True,
        'min_data_points': 10  # Minimum number of data points to consider valid for visualizing
    }

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
            tickformat='%H:%M',
            nticks=12,  # Show approximately 5-minute intervals for 60-minute data
            tickangle=-45,
            showgrid=True
        )
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
        title = 'Predicted Bitcoin Price with Confidence Interval'
    else:
        title = 'Bitcoin Price Data (No Data Available)'
    
    # Update layout
    layout_update = {
        'title': title,
        'xaxis_title': 'Time',
        'yaxis_title': 'Actual Price (USD)',
        'template': 'plotly_white',
        'height': config['dashboard']['chart_height'],
        'showlegend': True,
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        'yaxis': dict(
            autorange=True,
            range=y_range,
            tickformat=",.0f",
            tickprefix="$",
        ),
        'xaxis': dict(
            title='Time',
            tickformat='%H:%M',
            nticks=12,  # Show approximately 5-minute intervals for 60-minute data
            tickangle=-45,
            showgrid=True
        )
    }
    
    fig.update_layout(**layout_update)
    
    # Force x-axis range to show full 60 minutes if we have data
    if has_price_data:
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
            logger.info(f"Cold start mode (prediction chart): Using {time_span_minutes:.1f} minutes of data instead of {TIME_WINDOW_MINUTES}")
        else:
            # Standard mode: Use the full TIME_WINDOW_MINUTES range
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
                line=dict(color='green', width=2),
                hovertemplate='%{y:,.2f}'
            ))
            
            # Add zero line to show the baseline (perfect prediction)
            fig.add_trace(go.Scatter(
                x=[filtered_df['timestamp'].min(), filtered_df['timestamp'].max()],
                y=[0, 0],
                name='Perfect Prediction',
                line=dict(color='gray', width=1, dash='dash')
            ))
            
            # Calculate average error and RMSE
            avg_error = filtered_df['actual_error'].mean()
            mse = (filtered_df['actual_error'] ** 2).mean()
            rmse = np.sqrt(mse)
            
            # Add a horizontal line for the average error
            fig.add_trace(go.Scatter(
                x=[filtered_df['timestamp'].min(), filtered_df['timestamp'].max()],
                y=[avg_error, avg_error],
                name=f'Avg Error: {avg_error:.2f}',
                line=dict(color='blue', width=1, dash='dash')
            ))
            
            # Calculate percentage errors for display
            if 'rmse' in filtered_df.columns:
                filtered_df['pct_error'] = (filtered_df['actual_error'] / filtered_df['rmse']) * 100
                
                # Remove this annotation to avoid legend overlap and confusion
                # avg_pct_error = filtered_df['pct_error'].mean()
                # fig.add_annotation(
                #     x=filtered_df['timestamp'].max(),
                #     y=filtered_df['actual_error'].max(),
                #     text=f"Avg % Error: {avg_pct_error:.2f}%<br>RMSE: {rmse:.2f}",
                #     showarrow=False,
                #     yshift=10,
                #     bgcolor="rgba(255, 255, 255, 0.8)",
                #     bordercolor="gray",
                #     borderwidth=1
                # )
        
        if has_mae:
            # Also show MAE on the same chart but with lighter opacity
            filtered_df['mae'] = pd.to_numeric(filtered_df['mae'], errors='coerce')
            filtered_df = filtered_df.dropna(subset=['mae'])
            
            # Filter out extreme outliers in MAE
            median_mae = filtered_df['mae'].median()
            q1 = filtered_df['mae'].quantile(0.25)
            q3 = filtered_df['mae'].quantile(0.75)
            iqr = q3 - q1
            upper_threshold = median_mae + 3 * iqr
            
            mae_filtered_df = filtered_df[filtered_df['mae'] <= upper_threshold].copy()
            
            # If we filtered out too many points (>50%), use a simpler approach
            if len(mae_filtered_df) < len(filtered_df) * 0.5:
                # Fall back to using the 95th percentile as the cutoff
                p95 = filtered_df['mae'].quantile(0.95)
                mae_filtered_df = filtered_df[filtered_df['mae'] <= p95].copy()
            
    fig.add_trace(go.Scatter(
                x=mae_filtered_df['timestamp'],
                y=mae_filtered_df['mae'],
        name='MAE',
                line=dict(color='orange', width=2, dash='dot'),
                opacity=0.7,
                hovertemplate='%{y:,.2f}'
    ))
    
    fig.update_layout(
        title='Prediction Error Over Time',
        yaxis_title='Error (USD)',
        xaxis_title='Time',
        template='plotly_white',
        height=int(config['dashboard']['chart_height'] * 0.7),
        showlegend=True,
        yaxis=dict(
            tickformat=',.0f',
            tickprefix='$',
            ticksuffix='',
            tickmode='auto',
        ),
        xaxis=dict(
            title='Time',
            tickformat='%H:%M',
            nticks=12,  # Show approximately 5-minute intervals for 60-minute data
            tickangle=-45,
            showgrid=True
        )
    )
    
    # Force x-axis range to show full 60 minutes if we have data
    if metrics_df is not None and not metrics_df.empty:
        # Get the timestamp range
        max_time = metrics_df['timestamp'].max()
        
        # Check if we're in a cold start scenario (less than the full time window)
        time_span_minutes = (metrics_df['timestamp'].max() - metrics_df['timestamp'].min()).total_seconds() / 60
        data_points = len(metrics_df)
        
        # Cold start handling: For less than TIME_WINDOW_MINUTES of data, use all available data
        if config['dashboard']['cold_start']['enabled'] and time_span_minutes < TIME_WINDOW_MINUTES and data_points >= config['dashboard']['cold_start']['min_data_points']:
            # Use the actual data range with a small padding
            min_time = metrics_df['timestamp'].min()
            padding = pd.Timedelta(seconds=30)  # Add 30 seconds padding
            fig.update_xaxes(range=[min_time - padding, max_time + padding])
            logger.info(f"Cold start mode (error chart): Using {time_span_minutes:.1f} minutes of data instead of {TIME_WINDOW_MINUTES}")
        else:
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
            
            # Create histogram of errors
            fig.add_trace(go.Histogram(
                x=filtered_df['actual_error'],
                nbinsx=20,
                name='Error Distribution',
                marker_color='lightblue'
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
                    
                # Scale to match histogram height
                hist_max = np.histogram(filtered_df['actual_error'], bins=20)[0].max()
                norm_max = max(y_norm) if len(y_norm) > 0 else 1
                scale_factor = hist_max / norm_max if norm_max > 0 else 1
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_norm * scale_factor,
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
            tickformat=',.0f',
            tickprefix='$',
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2
        )
    )
    
    return fig

def main():
    """Main dashboard function."""
    st.title("Bitcoin Price Dashboard")
    
    # Create placeholders for dynamic content
    metrics_placeholder = st.empty()
    price_placeholder = st.empty()
    prediction_placeholder = st.empty()
    mae_placeholder = st.empty()
    distribution_placeholder = st.empty()
    
    # Sidebar configuration
    st.sidebar.title("Dashboard Settings")
    
    # Display the time window setting
    st.sidebar.info(f"Target chart window: {TIME_WINDOW_MINUTES} minutes")
    
    # Cold start mode information
    if config['dashboard']['cold_start']['enabled']:
        st.sidebar.success(
            "Cold start mode is enabled. For new systems with less than "
            f"{TIME_WINDOW_MINUTES} minutes of data, charts will automatically "
            "adjust to show all available data."
        )
    else:
        st.sidebar.info(
            "Cold start mode is disabled. Charts will always show exactly "
            f"{TIME_WINDOW_MINUTES} minutes of data."
        )
    
    # Add information for status
    status_placeholder = st.sidebar.empty()
    
    # Main dashboard loop
    while True:
        try:
            # Load all data
            price_df, pred_df, metrics_df = load_data()
            
            # Generate a unique timestamp for this iteration to avoid duplicate keys
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Log data info after loading
            logger.info(f"Raw data loaded - price: {len(price_df)} rows, predictions: {len(pred_df)} rows, metrics: {len(metrics_df)} rows")
            
            # Filter price data by actual time using consistent TIME_WINDOW_MINUTES
            price_df = filter_last_n_minutes(price_df, TIME_WINDOW_MINUTES, check_time=True)
            
            # Check if we're in cold start mode for status display
            is_cold_start = False
            cold_start_minutes = 0
            if config['dashboard']['cold_start']['enabled'] and not price_df.empty and len(price_df) >= config['dashboard']['cold_start']['min_data_points']:
                time_span_minutes = (price_df['timestamp'].max() - price_df['timestamp'].min()).total_seconds() / 60
                if time_span_minutes < TIME_WINDOW_MINUTES:
                    is_cold_start = True
                    cold_start_minutes = time_span_minutes
            
            # Update status in sidebar
            if is_cold_start:
                status_placeholder.warning(
                    f"Cold start mode active: Showing {cold_start_minutes:.1f} minutes of data. "
                    f"Full {TIME_WINDOW_MINUTES}-minute view will be used once sufficient data is available."
                )
            else:
                status_placeholder.info(f"Normal mode: Showing {TIME_WINDOW_MINUTES} minutes of data")
            
            # Check if timestamps in prediction data match the price data timeframe
            timestamps_match = False
            if not price_df.empty and not pred_df.empty:
                # Get time ranges
                price_min_time = price_df['timestamp'].min()
                price_max_time = price_df['timestamp'].max()
                pred_min_time = pred_df['timestamp'].min()
                pred_max_time = pred_df['timestamp'].max()
                
                # Check if there's any overlap in the time ranges
                if (pred_min_time <= price_max_time and pred_max_time >= price_min_time):
                    timestamps_match = True
                    logger.info("Found overlapping timestamps between price and prediction data")
                else:
                    logger.info(f"No timestamp overlap: Price: {price_min_time} to {price_max_time}, Pred: {pred_min_time} to {pred_max_time}")
            
            # Filter prediction data to match the same time window
            if pred_df is not None and not pred_df.empty:
                # First sort by timestamp
                pred_df = pred_df.sort_values('timestamp')
                # Filter to the same time window as price data
                if price_df is not None and not price_df.empty:
                    price_min_time = price_df['timestamp'].min()
                    pred_df = pred_df[pred_df['timestamp'] >= price_min_time]
                # If no data in time window, use latest data
                if pred_df.empty:
                    pred_df = pred_df.sort_values('timestamp').tail(30)  # Get latest 30 predictions
                
            # Filter metrics data to match the same time window
            if metrics_df is not None and not metrics_df.empty:
                # First sort by timestamp
                metrics_df = metrics_df.sort_values('timestamp')
                # Filter to the same time window as price data
                if price_df is not None and not price_df.empty:
                    price_min_time = price_df['timestamp'].min()
                    metrics_df = metrics_df[metrics_df['timestamp'] >= price_min_time]
                # If no data in time window, use latest data
                if metrics_df.empty:
                    metrics_df = metrics_df.sort_values('timestamp').tail(30)  # Get latest 30 metrics
            
            # Log data info after filtering
            logger.info(f"After filtering - price: {len(price_df)} rows, predictions: {len(pred_df)} rows, metrics: {len(metrics_df)} rows")
            
            # Display metrics if price data is available
            if price_df is not None and not price_df.empty and 'close' in price_df.columns:
                latest_price = price_df['close'].iloc[-1]
                latest_time = price_df['timestamp'].iloc[-1]
                
                with metrics_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    
                    # Price metric
                    with col1:
                        if len(price_df) > 1:
                            price_diff = price_df['close'].iloc[-1] - price_df['close'].iloc[-2]
                        else:
                            price_diff = 0
                        st.metric(
                            "Latest Price",
                            usd_to_display_str(latest_price),
                            usd_to_display_str(price_diff)
                        )
                    
                    # Last update time
                    with col2:
                        st.metric(
                            "Last Update",
                            latest_time.strftime("%Y-%m-%dT%H:%M:%S")
                        )
                    
                    # Prediction metric (if available)
                    with col3:
                        if pred_df is not None and not pred_df.empty and 'pred_price' in pred_df.columns:
                            # Always use the latest prediction value regardless of timestamp
                            latest_pred = pred_df['pred_price'].iloc[-1]
                            latest_pred_time = pred_df['timestamp'].iloc[-1]
                            
                            # Ensure we can compare dates regardless of string or datetime format
                            # Format the display time in consistent format
                            if isinstance(latest_pred_time, str):
                                latest_pred_time = pd.to_datetime(latest_pred_time)
                            
                            if isinstance(latest_time, str):
                                latest_time = pd.to_datetime(latest_time)
                                
                            # Show prediction value with appropriate label
                            if latest_pred_time.date() != latest_time.date():
                                # Use T format for consistency
                                display_time = format_timestamp(latest_pred_time, use_t_separator=True)
                                prediction_label = f"Prediction ({display_time.split('T')[0]})"
                            else:
                                prediction_label = "Latest Prediction"
                                
                            if len(pred_df) > 1:
                                pred_diff = pred_df['pred_price'].iloc[-1] - pred_df['pred_price'].iloc[-2]
                            else:
                                pred_diff = 0
                                
                            st.metric(
                                prediction_label,
                                usd_to_display_str(latest_pred),
                                usd_to_display_str(pred_diff)
                            )
                        else:
                            st.metric("Latest Prediction", "No data", "")
                
                # Always show price chart if available
                with price_placeholder:
                    st.plotly_chart(create_price_chart(price_df), use_container_width=True, key=f"price_chart_{timestamp_str}")
                
                # Show prediction chart (will use dual-axis if timestamps don't match)
                with prediction_placeholder:
                    st.plotly_chart(create_prediction_chart(price_df, pred_df), use_container_width=True, key=f"prediction_chart_{timestamp_str}")
                
                # Show MAE chart if available
                with mae_placeholder:
                    if metrics_df is not None and not metrics_df.empty and 'mae' in metrics_df.columns:
                        st.plotly_chart(create_mae_chart(metrics_df), use_container_width=True, key=f"mae_chart_{timestamp_str}")
                        
                        # Show error distribution chart below the MAE chart
                        if 'actual_error' in metrics_df.columns:
                            with distribution_placeholder:
                                st.plotly_chart(create_error_distribution_chart(metrics_df), use_container_width=True, key=f"distribution_chart_{timestamp_str}")
                    else:
                        st.info("No prediction error metrics available")
            else:
                # Show placeholders if no data available
                with metrics_placeholder:
                    st.info("Waiting for price data...")
                with price_placeholder:
                    st.plotly_chart(create_price_chart(pd.DataFrame()), use_container_width=True, key=f"empty_price_chart_{timestamp_str}")
                with prediction_placeholder:
                    st.plotly_chart(create_prediction_chart(pd.DataFrame(), pd.DataFrame()), use_container_width=True, key=f"empty_prediction_chart_{timestamp_str}")
                with mae_placeholder:
                    st.info("No metrics data available")
            
            # Wait for next update
            time.sleep(REFRESH_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}\n{traceback.format_exc()}")
            with st.container():
                st.error(f"Error updating dashboard: {e}")
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main() 