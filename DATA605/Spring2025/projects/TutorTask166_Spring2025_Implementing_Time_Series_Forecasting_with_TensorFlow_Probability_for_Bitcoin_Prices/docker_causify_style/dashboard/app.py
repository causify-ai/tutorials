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
import yaml
import os
import logging
from utilities.data_loader import load_and_filter_data
from utilities.price_format import usd_to_display_str
from utilities.timestamp_format import parse_timestamp

# Load configuration
with open('/app/configs/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Set page config
st.set_page_config(
    page_title="Bitcoin Price Dashboard",
    page_icon="📈",
    layout="wide"
)

# Constants
# REFRESH_INTERVAL = 0.1  # seconds, more frequent updates
REFRESH_INTERVAL = config['dashboard']['refresh_interval']  # = 1 second by default
PRICE_FILE = config['data']['raw_data']['instant_data']['file']
PREDICTIONS_FILE = config['data']['predictions']['instant_data']['predictions_file']
METRICS_FILE = config['data']['predictions']['instant_data']['metrics_file']

logger = logging.getLogger(__name__)

@st.cache_data(ttl=config['dashboard']['refresh_interval'])
def load_data():
    """Load the latest data with caching."""
    try:
        # Load price data
        if not os.path.exists(PRICE_FILE):
            st.warning("Price data file not found")
            return None, None, None
        price_df = pd.read_csv(
            PRICE_FILE,
            names=config['data_format']['columns']['raw_data']['names'],
            skiprows=1,
            parse_dates=['timestamp'],
            date_format=config['data_format']['timestamp']['format']
        )
        # Load predictions if available
        if os.path.exists(PREDICTIONS_FILE):
            pred_df = pd.read_csv(
                PREDICTIONS_FILE,
                names=config['data_format']['columns']['predictions']['names'],
                skiprows=1,
                parse_dates=['timestamp'],
                date_format=config['data_format']['timestamp']['format']
            )
        else:
            pred_df = None
        # Load metrics if available
        if os.path.exists(METRICS_FILE):
            metrics_df = pd.read_csv(
                METRICS_FILE,
                names=config['data_format']['columns']['metrics']['names'],
                skiprows=1,
                parse_dates=['timestamp'],
                date_format=config['data_format']['timestamp']['format']
            )
        else:
            metrics_df = None
        return price_df, pred_df, metrics_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")
        return None, None, None

def filter_last_n_minutes(df, n_minutes):
    if df is None or df.empty:
        return df
    # Parse timestamps using utility
    df = df.copy()
    df['timestamp'] = df['timestamp'].apply(parse_timestamp)
    now = pd.Timestamp.now(tz=None)
    cutoff = now - pd.Timedelta(minutes=n_minutes)
    return df[df['timestamp'] >= cutoff]

def create_price_chart(price_df):
    """Create candlestick chart for actual price."""
    fig = go.Figure()
    
    if price_df is not None and not price_df.empty:
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
    
    # Update layout
    fig.update_layout(
        title='Bitcoin Price (Candlestick Chart)',
        yaxis_title='Price (USD)',
        xaxis_title='Time',
        template='plotly_white',
        height=config['dashboard']['chart_height'],
        showlegend=False,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_prediction_chart(price_df, pred_df):
    """Create prediction comparison chart with confidence interval."""
    fig = go.Figure()
    if price_df is not None and not price_df.empty:
        fig.add_trace(go.Scatter(
            x=price_df['timestamp'],
            y=price_df['close'],
            name='Actual Price',
            line=dict(color=config['dashboard']['colors']['actual'], width=2)
        ))
    if pred_df is not None and not pred_df.empty:
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['pred_price'],
            name='Predicted Price',
            line=dict(color=config['dashboard']['colors']['predicted'], width=2)
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['pred_upper'],
            name='Upper Bound',
            line=dict(color=config['dashboard']['colors']['confidence'], dash='dash'),
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['pred_lower'],
            name='Lower Bound',
            fill='tonexty',
            line=dict(color=config['dashboard']['colors']['confidence'], dash='dash'),
            showlegend=True
        ))
    # Compute y-axis range with margin
    all_y = []
    if price_df is not None and not price_df.empty:
        all_y.extend(price_df['close'].values)
    if pred_df is not None and not pred_df.empty:
        all_y.extend(pred_df['pred_price'].values)
        all_y.extend(pred_df['pred_upper'].values)
        all_y.extend(pred_df['pred_lower'].values)
    if all_y:
        y_min, y_max = min(all_y), max(all_y)
        margin = (y_max - y_min) * 0.02 if y_max > y_min else 1
        y_range = [y_min - margin, y_max + margin]
    else:
        y_range = None
    fig.update_layout(
        title='Predicted Price with Confidence Interval vs Actual',
        yaxis_title='Price (USD)',
        xaxis_title='Time',
        template='plotly_white',
        height=config['dashboard']['chart_height'],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            autorange=True,
            range=y_range,
            tickformat=",.0f",
            tickprefix="$",
        )
    )
    return fig

def create_mae_chart(metrics_df):
    """Create MAE (Mean Absolute Error) chart as a separate line chart."""
    if metrics_df is None or metrics_df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=metrics_df['timestamp'],
        y=metrics_df['mae'],
        name='MAE',
        line=dict(color='orange', width=2)
    ))
    fig.update_layout(
        title='Prediction Error (MAE) Over Time',
        yaxis_title='Error (unitless)',
        xaxis_title='Time',
        template='plotly_white',
        height=int(config['dashboard']['chart_height'] * 0.7),
        showlegend=False,
        yaxis=dict(
            tickformat=',.0f',
            tickprefix='',
            ticksuffix='',
            tickmode='auto',
        )
    )
    return fig

def main():
    """Main dashboard function."""
    st.title("Bitcoin Price Dashboard")
    metrics_placeholder = st.empty()
    price_placeholder = st.empty()
    prediction_placeholder = st.empty()
    mae_placeholder = st.empty()
    time_window_minutes = config['dashboard']['plot_settings'].get('time_window_minutes', 30)
    while True:
        try:
            price_df, pred_df, metrics_df = load_data()
            # Filter all dataframes to last N minutes
            price_df = filter_last_n_minutes(price_df, time_window_minutes)
            pred_df = filter_last_n_minutes(pred_df, time_window_minutes)
            metrics_df = filter_last_n_minutes(metrics_df, time_window_minutes)
            if price_df is not None and not price_df.empty:
                latest_price = price_df['close'].iloc[-1]
                latest_time = price_df['timestamp'].iloc[-1]
                with metrics_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Latest Price",
                            usd_to_display_str(latest_price),
                            usd_to_display_str(price_df['close'].iloc[-1] - price_df['close'].iloc[-2])
                        )
                    with col2:
                        st.metric(
                            "Last Update",
                            latest_time.strftime("%Y-%m-%dT%H:%M:%S UTC")
                        )
                    with col3:
                        if pred_df is not None and not pred_df.empty:
                            latest_pred = pred_df['pred_price'].iloc[-1]
                            st.metric(
                                "Latest Prediction",
                                usd_to_display_str(latest_pred),
                                usd_to_display_str(pred_df['pred_price'].iloc[-1] - pred_df['pred_price'].iloc[-2])
                            )
                with price_placeholder:
                    st.plotly_chart(create_price_chart(price_df), use_container_width=True)
                with prediction_placeholder:
                    st.plotly_chart(create_prediction_chart(price_df, pred_df), use_container_width=True)
                with mae_placeholder:
                    st.plotly_chart(create_mae_chart(metrics_df), use_container_width=True)
            else:
                with metrics_placeholder:
                    st.info("Waiting for actual price data...")
                with price_placeholder:
                    st.plotly_chart(create_price_chart(pd.DataFrame()), use_container_width=True)
                with prediction_placeholder:
                    st.plotly_chart(create_prediction_chart(pd.DataFrame(), pd.DataFrame()), use_container_width=True)
                with mae_placeholder:
                    st.plotly_chart(create_mae_chart(pd.DataFrame()), use_container_width=True)
            time.sleep(REFRESH_INTERVAL)
        except Exception as e:
            st.error(f"Error updating dashboard: {e}")
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main() 