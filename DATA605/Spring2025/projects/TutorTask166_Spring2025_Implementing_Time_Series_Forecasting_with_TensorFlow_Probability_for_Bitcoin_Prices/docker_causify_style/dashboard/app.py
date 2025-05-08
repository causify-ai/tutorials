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
REFRESH_INTERVAL = 0.1  # seconds, more frequent updates
PRICE_FILE = config['data']['raw_data']['instant_data']['file']
PREDICTIONS_FILE = config['data']['predictions']['instant_data']['predictions_file']

logger = logging.getLogger(__name__)

@st.cache_data(ttl=config['dashboard']['refresh_interval'])
def load_data():
    """Load the latest data with caching."""
    try:
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        raw_data_file = config['data']['raw_data']['instant_data']['file']
        return load_and_filter_data(config, predictions_file, metrics_file, raw_data_file)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")
        return None, None

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
    """Create prediction comparison chart."""
    fig = go.Figure()
    
    if price_df is not None and not price_df.empty:
        # Add actual price
        fig.add_trace(go.Scatter(
            x=price_df['timestamp'],
            y=price_df['close'],
            name='Actual Price',
            line=dict(color=config['dashboard']['colors']['actual'], width=2)
        ))
    
    if pred_df is not None and not pred_df.empty:
        # Add predicted price
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['predicted_price'],
            name='Predicted Price',
            line=dict(color=config['dashboard']['colors']['predicted'], width=2)
        ))
        
        # Add confidence intervals
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['upper_bound'],
            name='Upper Bound',
            line=dict(color=config['dashboard']['colors']['confidence']),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['lower_bound'],
            name='Lower Bound',
            fill='tonexty',
            line=dict(color=config['dashboard']['colors']['confidence']),
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title='Price Predictions vs Actual',
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
        )
    )
    
    return fig

def main():
    """Main dashboard function."""
    st.title("Bitcoin Price Dashboard")
    
    # Create placeholder for metrics
    metrics_placeholder = st.empty()
    
    # Create placeholders for charts
    price_placeholder = st.empty()
    prediction_placeholder = st.empty()
    
    while True:
        try:
            # Load latest data
            price_df, pred_df = load_data()
            
            if price_df is not None and not price_df.empty:
                # Get latest price
                latest_price = price_df['close'].iloc[-1]
                latest_time = price_df['timestamp'].iloc[-1]
                
                # Update metrics
                with metrics_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Latest Price",
                            f"${latest_price:,.2f}",
                            f"{price_df['close'].iloc[-1] - price_df['close'].iloc[-2]:,.2f}"
                        )
                    with col2:
                        st.metric(
                            "Last Update",
                            latest_time.strftime("%Y-%m-%dT%H:%M:%S")  # Use ISO8601 format
                        )
                    with col3:
                        if pred_df is not None and not pred_df.empty:
                            latest_pred = pred_df['predicted_price'].iloc[-1]
                            st.metric(
                                "Latest Prediction",
                                f"${latest_pred:,.2f}",
                                f"{pred_df['predicted_price'].iloc[-1] - pred_df['predicted_price'].iloc[-2]:,.2f}"
                            )
                
                # Update charts
                with price_placeholder:
                    st.plotly_chart(create_price_chart(price_df), use_container_width=True)
                
                with prediction_placeholder:
                    st.plotly_chart(create_prediction_chart(price_df, pred_df), use_container_width=True)
            
            # Wait for next update
            time.sleep(REFRESH_INTERVAL)
            
        except Exception as e:
            st.error(f"Error updating dashboard: {e}")
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main() 