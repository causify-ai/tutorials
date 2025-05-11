"""
bitcoin_utils.py

This file contains utility functions that support the Bitcoin Data Pipeline project.

- Notebooks and DAG tasks should call these functions instead of writing logic inline.
- This keeps the code clean, reusable, and modular.
- Functions handle API data ingestion, time series processing, and AWS S3 storage.
"""

import requests
import boto3
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

# --------------------------------------------------------------------------
# Logging Setup
# --------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# File Paths (used inside Docker container)
# --------------------------------------------------------------------------

RAW_DATA_PATH = os.getenv("BITCOIN_RAW_PATH", "/opt/airflow/data/bitcoin_raw.csv")
PROCESSED_DATA_PATH = os.getenv("BITCOIN_PROCESSED_PATH", "/opt/airflow/data/bitcoin_processed.csv")

# --------------------------------------------------------------------------
# Function: Fetch real-time Bitcoin price from CoinGecko API
# --------------------------------------------------------------------------

def fetch_bitcoin_price():
    """
    Fetch current Bitcoin price in USD from CoinGecko.

    :return: Dictionary with UTC timestamp and price in USD
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()  # Raises exception if the request failed
    price_data = response.json()

    logger.info("Fetched Bitcoin price successfully.")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "price_usd": price_data["bitcoin"]["usd"]
    }

# --------------------------------------------------------------------------
# Function: Save fetched price to CSV (append if exists)
# --------------------------------------------------------------------------

def save_price_to_csv():
    """
    Fetch Bitcoin price and save it to RAW_DATA_PATH CSV file.

    Appends to existing file if it exists, otherwise creates a new one.
    """
    data = fetch_bitcoin_price()
    df = pd.DataFrame([data])

    if os.path.exists(RAW_DATA_PATH):
        df_existing = pd.read_csv(RAW_DATA_PATH)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_csv(RAW_DATA_PATH, index=False)
    logger.info(f"Saved price to {RAW_DATA_PATH}")

# --------------------------------------------------------------------------
# Function: Compute moving average and save to new CSV
# --------------------------------------------------------------------------

def compute_moving_average(window=2):
    """
    Compute a rolling moving average of the Bitcoin price.

    :param window: Rolling window size for the moving average (default = 2)
    :return: None (writes result to PROCESSED_DATA_PATH)
    """
    if not os.path.exists(RAW_DATA_PATH):
        logger.error("Raw data file not found.")
        return

    df = pd.read_csv(RAW_DATA_PATH)
    df['price_ma'] = df['price_usd'].rolling(window=window).mean()
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Processed data saved to {PROCESSED_DATA_PATH}")

# --------------------------------------------------------------------------
# Function: Upload processed file to AWS S3
# --------------------------------------------------------------------------

def upload_to_s3(bucket_name, key_path):
    """
    Upload the processed CSV file to a specified S3 bucket/path.

    :param bucket_name: Name of the target S3 bucket
    :param key_path: S3 key (file path inside the bucket)
    :return: None
    """
    try:
        logger.info("Uploading to S3...")
        s3 = boto3.client('s3')
        s3.upload_file(PROCESSED_DATA_PATH, bucket_name, key_path)
        logger.info(f" Uploaded to s3://{bucket_name}/{key_path}")
    except Exception as e:
        logger.error(f" Upload failed: {e}")
        raise
