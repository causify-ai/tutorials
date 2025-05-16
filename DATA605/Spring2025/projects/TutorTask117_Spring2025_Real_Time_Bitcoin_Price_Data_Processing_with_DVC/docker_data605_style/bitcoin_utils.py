# bitcoin_utils.py

# Wrapper module to expose key functions for notebooks

from src.live_fetcher import fetch_price
from src.data_ingestion import record_price
from src.preprocess_eda import preprocess, plot_data
