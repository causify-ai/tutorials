#!/usr/bin/env python3
"""
Real-time Bitcoin price dashboard using Streamlit.
Displays OHLCV data from CSV and Kafka in real-time.
"""
import os
import yaml
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

# Load configuration
with open('/app/configs/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Set page config
st.set_page_config(
    page_title="Bitcoin Price Dashboard",
    page_icon="📈",
    layout="wide"
)

# Add title
st.title("Real-time Bitcoin Price Dashboard")

# Function to load data
@st.cache_data(ttl=5)  # Cache for 5 seconds
def load_data():
    try:
        df = pd.read_csv(config['data']['raw_data']['instant_data']['file'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Function to load predictions
@st.cache_data(ttl=5)  # Cache for 5 seconds
def load_predictions():
    try:
        if not os.path.exists(config['data']['predictions']['instant_data']['predictions_file']):
            return pd.DataFrame()
        df = pd.read_csv(config['data']['predictions']['instant_data']['predictions_file'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        return pd.DataFrame()

# Create candlestick chart
def create_candlestick_chart(df):
    if df.empty:
        return None
    
    # Get the last 24 hours of data
    end_time = df['timestamp'].max()
    start_time = end_time - timedelta(hours=24)
    mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
    df_filtered = df.loc[mask]
    
    # Resample to 1-minute intervals
    df_resampled = df_filtered.set_index('timestamp').resample('1T').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    fig = go.Figure(data=[go.Candlestick(
        x=df_resampled.index,
        open=df_resampled['open'],
        high=df_resampled['high'],
        low=df_resampled['low'],
        close=df_resampled['close']
    )])
    
    fig.update_layout(
        title="Bitcoin Price (Last 24 Hours)",
        yaxis_title="Price (USD)",
        xaxis_title="Time",
        height=600,
        template="simple_white"
    )
    
    return fig

# Create volume chart
def create_volume_chart(df):
    if df.empty:
        return None
    
    # Get the last 24 hours of data
    end_time = df['timestamp'].max()
    start_time = end_time - timedelta(hours=24)
    mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
    df_filtered = df.loc[mask]
    
    # Resample to 1-minute intervals
    df_resampled = df_filtered.set_index('timestamp').resample('1T').agg({
        'volume': 'sum'
    }).dropna()
    
    fig = go.Figure(data=[go.Bar(
        x=df_resampled.index,
        y=df_resampled['volume'],
        name="Volume"
    )])
    
    fig.update_layout(
        title="Trading Volume (Last 24 Hours)",
        yaxis_title="Volume (BTC)",
        xaxis_title="Time",
        height=300,
        template="simple_white"
    )
    
    return fig

# Create prediction comparison chart
def create_prediction_chart(df, predictions_df):
    if df.empty:
        return None
    
    # Get the last 24 hours of data
    end_time = df['timestamp'].max()
    start_time = end_time - timedelta(hours=24)
    mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
    df_filtered = df.loc[mask]
    
    fig = go.Figure()
    
    # Add actual price line
    fig.add_trace(go.Scatter(
        x=df_filtered['timestamp'],
        y=df_filtered['close'],
        name='Actual Price',
        line=dict(color='blue')
    ))
    
    # Add predictions if available
    if not predictions_df.empty:
        # Filter predictions for the same time range
        pred_mask = (predictions_df['timestamp'] >= start_time) & (predictions_df['timestamp'] <= end_time)
        pred_filtered = predictions_df.loc[pred_mask]
        
        if not pred_filtered.empty:
            # Add predicted price line
            fig.add_trace(go.Scatter(
                x=pred_filtered['timestamp'],
                y=pred_filtered['predicted_price'],
                name='Predicted Price',
                line=dict(color='red')
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=pred_filtered['timestamp'],
                y=pred_filtered['upper_bound'],
                name='Upper Bound',
                line=dict(color='rgba(255,0,0,0.2)'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=pred_filtered['timestamp'],
                y=pred_filtered['lower_bound'],
                name='Lower Bound',
                line=dict(color='rgba(255,0,0,0.2)'),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)',
                showlegend=False
            ))
    
    fig.update_layout(
        title="Price Prediction Comparison (Last 24 Hours)",
        yaxis_title="Price (USD)",
        xaxis_title="Time",
        height=400,
        template="simple_white",
        hovermode='x unified'
    )
    
    return fig

# Main dashboard layout
def main():
    # Add metrics container
    metrics_container = st.container()
    
    # Add charts
    chart_container = st.container()
    
    # Create two columns for the charts
    col1, col2 = st.columns([2, 1])
    
    while True:
        try:
            # Load latest data
            df = load_data()
            predictions_df = load_predictions()
            
            if not df.empty:
                # Update metrics
                with metrics_container:
                    latest = df.iloc[-1]
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"${latest['close']:,.2f}")
                    with col2:
                        st.metric("24h High", f"${df['high'].max():,.2f}")
                    with col3:
                        st.metric("24h Low", f"${df['low'].min():,.2f}")
                    with col4:
                        st.metric("24h Volume", f"{df['volume'].sum():,.4f} BTC")
                
                # Update charts
                with chart_container:
                    with col1:
                        candlestick_chart = create_candlestick_chart(df)
                        if candlestick_chart:
                            st.plotly_chart(candlestick_chart, use_container_width=True)
                    
                    with col2:
                        volume_chart = create_volume_chart(df)
                        if volume_chart:
                            st.plotly_chart(volume_chart, use_container_width=True)
                    
                    # Add prediction comparison chart
                    prediction_chart = create_prediction_chart(df, predictions_df)
                    if prediction_chart:
                        st.plotly_chart(prediction_chart, use_container_width=True)
            
            # Wait for 5 seconds before refreshing
            st.empty()
            st.rerun()
            
        except Exception as e:
            st.error(f"Error updating dashboard: {e}")
            st.rerun()

if __name__ == "__main__":
    main() 