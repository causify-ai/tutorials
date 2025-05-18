import streamlit as st
from src.data_collector import DataCollector
import pandas as pd

st.title("Bitcoin Data Loading Test")

st.write("Testing data collection from different sources...")

# Test CoinGecko
try:
    st.subheader("CoinGecko Data Source")
    with st.spinner("Loading data from CoinGecko..."):
        dc_coingecko = DataCollector(source='coingecko')
        data_coingecko = dc_coingecko.get_historical_data(period='7d')
        
        if not data_coingecko.empty:
            st.success("✅ Successfully loaded data from CoinGecko")
            st.write(f"Retrieved {len(data_coingecko)} records")
            st.dataframe(data_coingecko.head())
        else:
            st.error("❌ No data retrieved from CoinGecko")
except Exception as e:
    st.error(f"❌ Error loading data from CoinGecko: {str(e)}")
    
# Test YFinance
try:
    st.subheader("Yahoo Finance Data Source")
    with st.spinner("Loading data from Yahoo Finance..."):
        dc_yfinance = DataCollector(source='yfinance')
        data_yfinance = dc_yfinance.get_historical_data(period='7d')
        
        if not data_yfinance.empty:
            st.success("✅ Successfully loaded data from Yahoo Finance")
            st.write(f"Retrieved {len(data_yfinance)} records")
            st.dataframe(data_yfinance.head())
        else:
            st.error("❌ No data retrieved from Yahoo Finance")
except Exception as e:
    st.error(f"❌ Error loading data from Yahoo Finance: {str(e)}")