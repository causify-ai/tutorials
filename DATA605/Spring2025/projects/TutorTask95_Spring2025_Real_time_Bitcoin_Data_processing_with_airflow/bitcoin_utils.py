'''
This file contains utility functions that support the Bitcoin Data Pipeline project.

Core functionalities:
- Real-time Bitcoin price ingestion from CoinGecko API
- Anomaly detection with configurable thresholds
- Rolling statistics: mean and std deviation
- Uploading raw/processed data to AWS S3
- Slack alerts for anomalies
- Archival utilities for old CSV snapshots

'''

import requests
import boto3
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from botocore.exceptions import BotoCoreError, ClientError

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File Paths
RAW_DATA_PATH = os.getenv("BITCOIN_RAW_PATH", "/opt/airflow/data/bitcoin_raw.csv")
PROCESSED_DATA_PATH = os.getenv("BITCOIN_PROCESSED_PATH", "/opt/airflow/data/bitcoin_processed.csv")
ARCHIVE_PATH = os.getenv("BITCOIN_ARCHIVE_PATH", "/opt/airflow/data/archive")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Function: Send Slack alert
def send_slack_alert(message):
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not set. Skipping alert.")
        return
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        if response.status_code != 200:
            logger.warning(f"Slack alert failed: {response.text}")
        else:
            logger.info("Slack alert sent.")
    except Exception as e:
        logger.error(f"Slack notification error: {e}")

#  Fetch real-time Bitcoin price from CoinGecko API
def fetch_bitcoin_price():
    url = (
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        "&include_24hr_change=true&include_1hr_change=true"
    )
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    response = session.get(url)
    response.raise_for_status()
    price_data = response.json()

    logger.info("Fetched Bitcoin price successfully.")
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "price_usd": price_data["bitcoin"]["usd"],
        "change_1h": price_data["bitcoin"].get("usd_1h_change"),
        "change_24h": price_data["bitcoin"].get("usd_24h_change"),
    }

# Save fetched price to CSV and upload raw to S3
def save_price_to_csv(threshold=5):
    data = fetch_bitcoin_price()

    change_1h = float(data.get("change_1h") or 0)
    change_24h = float(data.get("change_24h") or 0)

    alerts = []
    if abs(change_1h) > threshold:
        msg = f" 1h anomaly: {change_1h:.2f}%"
        logger.warning(msg)
        alerts.append(msg)
    if abs(change_24h) > threshold:
        msg = f" 24h anomaly: {change_24h:.2f}%"
        logger.warning(msg)
        alerts.append(msg)

    if alerts:
        send_slack_alert("\n".join(alerts))

    data["change_1h"] = change_1h
    data["change_24h"] = change_24h

    df = pd.DataFrame([data])
    if os.path.exists(RAW_DATA_PATH):
        df_existing = pd.read_csv(RAW_DATA_PATH)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_csv(RAW_DATA_PATH, index=False)
    logger.info(f"Saved price to {RAW_DATA_PATH}")

    try:
        s3 = boto3.client('s3')
        s3.upload_file(RAW_DATA_PATH, 'bitcoin-price-store', 'raw/bitcoin_raw.csv')
        logger.info("Uploaded raw CSV to s3://bitcoin-price-store/raw/bitcoin_raw.csv")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Raw S3 upload failed: {e}")

# Compute rolling stats and upload processed CSV to S3
def compute_moving_average(window=2):
    if not os.path.exists(RAW_DATA_PATH):
        logger.error("Raw data file not found.")
        return

    df = pd.read_csv(RAW_DATA_PATH)
    if 'price_usd' not in df.columns:
        logger.error("Missing 'price_usd' column in data.")
        return

    df['price_ma'] = df['price_usd'].rolling(window=window).mean()
    df['price_std'] = df['price_usd'].rolling(window=window).std()

    df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Processed data saved to {PROCESSED_DATA_PATH}")

    try:
        s3 = boto3.client('s3')
        s3.upload_file(PROCESSED_DATA_PATH, 'bitcoin-price-store', 'processed/bitcoin_processed.csv')
        logger.info("Uploaded processed CSV to s3://bitcoin-price-store/processed/bitcoin_processed.csv")
    except Exception as e:
        logger.warning(f"Processed CSV upload failed: {e}")

# Manual S3 upload utility
def upload_to_s3(bucket_name, key_path):
    try:
        logger.info("Uploading to S3...")
        s3 = boto3.client('s3')
        s3.upload_file(PROCESSED_DATA_PATH, bucket_name, key_path)
        logger.info(f"Uploaded to s3://{bucket_name}/{key_path}")
    except (BotoCoreError, ClientError, FileNotFoundError) as e:
        logger.error(f"Upload failed: {e}")
        raise

# Archive snapshot copy of raw file
def archive_raw_snapshot():
    if not os.path.exists(RAW_DATA_PATH):
        logger.error("No raw CSV to archive.")
        return

    if not os.path.exists(ARCHIVE_PATH):
        os.makedirs(ARCHIVE_PATH)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive_file = os.path.join(ARCHIVE_PATH, f"bitcoin_raw_snapshot_{timestamp}.csv")
    df = pd.read_csv(RAW_DATA_PATH)
    df.to_csv(archive_file, index=False)
    logger.info(f"Archived raw snapshot to {archive_file}")

    try:
        s3 = boto3.client('s3')
        s3.upload_file(archive_file, 'bitcoin-price-store', f"archive/{os.path.basename(archive_file)}")
        logger.info(f"Uploaded archive snapshot to S3: s3://bitcoin-price-store/archive/{os.path.basename(archive_file)}")
    except Exception as e:
        logger.warning(f"Archive snapshot upload failed: {e}")
