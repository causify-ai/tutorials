# bitcoin_emr_utils.py

import requests
import boto3
import json
from datetime import datetime
import pytz

# Get current UTC timestamp in ISO format
def get_current_timestamp():
    return datetime.now(pytz.UTC).isoformat()

# Fetch Bitcoin price from CoinGecko (or your chosen API)
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['bitcoin']['usd']

# Save a price record to S3 as JSON
def save_price_to_s3(bucket, folder, filename_prefix="price", price_usd=None):
    s3 = boto3.client('s3')
    timestamp = get_current_timestamp()
    if price_usd is None:
        price_usd = fetch_bitcoin_price()
    
    record = {
        "timestamp": timestamp,
        "price_usd": price_usd
    }

    key = f"{folder}/{filename_prefix}_{timestamp}.json"
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(record))
    print(f"✅ Uploaded: {key}")
