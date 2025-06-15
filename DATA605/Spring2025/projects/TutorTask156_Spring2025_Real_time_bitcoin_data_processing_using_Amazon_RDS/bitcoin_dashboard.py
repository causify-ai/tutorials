import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import bitcoin_rds_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bitcoin_rds_utils import (
    get_db_connection,
    calculate_moving_average
)

def get_most_recent_bitcoin_price(conn):
    """Get the most recent Bitcoin price from the database"""
    query = """
    SELECT price_usd
    FROM raw_bitcoin_prices
    ORDER BY timestamp DESC
    LIMIT 1;
    """
    try:
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            return df['price_usd'].iloc[0]
        return "N/A"
    except Exception as e:
        st.error(f"Error fetching latest Bitcoin price: {e}")
        return "N/A"

def get_bitcoin_price_for_days(conn, days):
    """Get Bitcoin price data for the specified number of days"""
    query = """
    SELECT timestamp, price_usd 
    FROM raw_bitcoin_prices
    WHERE timestamp > NOW() - INTERVAL '%s days'
    ORDER BY timestamp;
    """
    try:
        df = pd.read_sql_query(query, conn, params=(days,))
        return df
    except Exception as e:
        st.error(f"Error fetching Bitcoin price data: {e}")
        return pd.DataFrame()

def get_bitcoin_volume_for_days(conn, days):
    """Get Bitcoin trading volume data for the specified number of days"""
    query = """
    SELECT timestamp, volume_usd as volume
    FROM raw_bitcoin_prices
    WHERE timestamp > NOW() - INTERVAL '%s days'
    ORDER BY timestamp;
    """
    try:
        df = pd.read_sql_query(query, conn, params=(days,))
        return df
    except Exception as e:
        st.error(f"Error fetching Bitcoin volume data: {e}")
        return pd.DataFrame()

def main():
    st.title("Bitcoin Dashboard")
    
    # Sidebar with days slider
    st.sidebar.header("Settings")
    days = st.sidebar.slider("Select number of days", 1, 60, 30)
    
    # Connect to RDS
    conn = get_db_connection()
    
    # Get latest and lowest price
    latest_price = get_most_recent_bitcoin_price(conn)
    
    # Get price data for selected days
    price_data = get_bitcoin_price_for_days(conn, days)
    lowest_price = price_data['price_usd'].min() if not price_data.empty else "N/A"
    
    # Display latest and lowest price
    col1, col2 = st.columns(2)
    col1.metric("Latest Bitcoin Price (USD)", f"${latest_price:.2f}" if isinstance(latest_price, (int, float)) else latest_price)
    col2.metric(f"Lowest Price (Last {days} days)", f"${lowest_price:.2f}" if isinstance(lowest_price, (int, float)) else lowest_price)
    
    # Price over time plot
    st.subheader(f"Bitcoin Price Over the Last {days} Days")
    if not price_data.empty:
        fig_price = px.line(price_data, x='timestamp', y='price_usd', title='Bitcoin Price (USD)')
        fig_price.update_layout(
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.warning("No price data available for the selected period")
    
    # Moving average plot
    st.subheader(f"Bitcoin Moving Averages (Last {days} Days)")
    if not price_data.empty and len(price_data) > 5:  # Need at least 5 days for moving averages
        # Calculate moving averages
        ma_data = price_data.copy()
        ma_data['MA5'] = ma_data['price_usd'].rolling(window=5).mean()
        ma_data['MA10'] = ma_data['price_usd'].rolling(window=10).mean() if days >= 10 else None
        ma_data['MA20'] = ma_data['price_usd'].rolling(window=20).mean() if days >= 20 else None
        
        # Create plot
        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(x=ma_data['timestamp'], y=ma_data['price_usd'], 
                                   mode='lines', name='Price'))
        fig_ma.add_trace(go.Scatter(x=ma_data['timestamp'], y=ma_data['MA5'], 
                                   mode='lines', name='5-Day MA'))
        
        if days >= 10:
            fig_ma.add_trace(go.Scatter(x=ma_data['timestamp'], y=ma_data['MA10'], 
                                       mode='lines', name='10-Day MA'))
        
        if days >= 20:
            fig_ma.add_trace(go.Scatter(x=ma_data['timestamp'], y=ma_data['MA20'], 
                                       mode='lines', name='20-Day MA'))
        
        fig_ma.update_layout(
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_ma, use_container_width=True)
    else:
        st.warning("Not enough data for moving averages")
    
    # Volume plot
    st.subheader(f"Bitcoin Trading Volume (Last {days} Days)")
    volume_data = get_bitcoin_volume_for_days(conn, days)
    if not volume_data.empty:
        fig_volume = px.bar(volume_data, x='timestamp', y='volume', title='Bitcoin Trading Volume')
        fig_volume.update_layout(
            xaxis_title='Date',
            yaxis_title='Volume (USD)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    else:
        st.warning("No volume data available for the selected period")
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main() 