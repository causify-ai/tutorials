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
REFRESH_INTERVAL = 1  # seconds
MAX_POINTS = 100  # Maximum number of points to display
PRICE_FILE = config['data']['raw_data']['instant_data']['file']
PREDICTIONS_FILE = config['data']['predictions']['instant_data']['predictions_file']

logger = logging.getLogger(__name__)

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    """Load the latest data with caching."""
    try:
        # Load price data with explicit column names
        price_df = pd.read_csv(
            PRICE_FILE,
            parse_dates=['timestamp'],
            names=['timestamp', 'open', 'high', 'low', 'close', 'volume'],
            skiprows=1  # Skip header row
        )
        
        # Load predictions if available
        pred_df = None
        if os.path.exists(PREDICTIONS_FILE):
            pred_df = pd.read_csv(
                PREDICTIONS_FILE,
                parse_dates=['timestamp'],
                names=['timestamp', 'actual_price', 'predicted_price', 'lower_bound', 'upper_bound'],
                skiprows=1  # Skip header row
            )
        
        return price_df, pred_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")
        return None, None

def create_candlestick_chart(price_df):
    """Create candlestick chart with real-time updates."""
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=price_df['timestamp'],
        open=price_df['open'],
        high=price_df['high'],
        low=price_df['low'],
        close=price_df['close'],
        name='Price'
    ))
    
    # Update layout
    fig.update_layout(
        title='Bitcoin Price',
        yaxis_title='Price (USD)',
        xaxis_title='Time',
        template='simple_white',
        height=600,
        showlegend=True
    )
    
    return fig

def create_prediction_chart(price_df, pred_df):
    """Create prediction comparison chart."""
    fig = go.Figure()
    
    # Add actual price
    fig.add_trace(go.Scatter(
        x=price_df['timestamp'],
        y=price_df['close'],
        name='Actual Price',
        line=dict(color='blue')
    ))
    
    # Add predictions if available
    if pred_df is not None and not pred_df.empty:
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['predicted_price'],
            name='Predicted Price',
            line=dict(color='red')
        ))
        
        # Add confidence intervals
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['upper_bound'],
            name='Upper Bound',
            line=dict(color='rgba(255,0,0,0.2)'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=pred_df['timestamp'],
            y=pred_df['lower_bound'],
            name='Lower Bound',
            line=dict(color='rgba(255,0,0,0.2)'),
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.1)',
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title='Price Predictions',
        yaxis_title='Price (USD)',
        xaxis_title='Time',
        template='simple_white',
        height=600,
        showlegend=True
    )
    
    return fig

def main():
    """Main dashboard function."""
    st.title("Bitcoin Price Dashboard")
    
    # Create placeholder for metrics
    metrics_placeholder = st.empty()
    
    # Create placeholders for charts
    candlestick_placeholder = st.empty()
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
                        st.metric("Latest Price", f"${latest_price:,.2f}")
                    with col2:
                        st.metric("Last Update", latest_time.strftime("%Y-%m-%d %H:%M:%S"))
                    with col3:
                        if pred_df is not None and not pred_df.empty:
                            latest_pred = pred_df['predicted_price'].iloc[-1]
                            st.metric("Latest Prediction", f"${latest_pred:,.2f}")
                
                # Update charts
                with candlestick_placeholder:
                    st.plotly_chart(create_candlestick_chart(price_df), use_container_width=True)
                
                with prediction_placeholder:
                    st.plotly_chart(create_prediction_chart(price_df, pred_df), use_container_width=True)
            
            # Wait for next update
            time.sleep(REFRESH_INTERVAL)
            
        except Exception as e:
            st.error(f"Error updating dashboard: {e}")
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main() 