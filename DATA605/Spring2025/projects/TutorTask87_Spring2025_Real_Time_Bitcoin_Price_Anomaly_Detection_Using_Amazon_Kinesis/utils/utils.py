# utils/utils.py

import boto3
import json
import requests
from datetime import datetime

# 1. Fetch real-time Bitcoin price
def fetch_bitcoin_price(api_url="https://api.coindesk.com/v1/bpi/currentprice/BTC.json"):
    """
    Fetch the current Bitcoin price in USD from an API.

    Args:
        api_url (str): API endpoint for Bitcoin price.

    Returns:
        dict: Bitcoin price data including price, timestamp, etc.
    """
    response = requests.get(api_url)
    data = response.json()

    price_usd = float(data["bpi"]["USD"]["rate"].replace(",", ""))
    timestamp = data["time"]["updatedISO"]

    return {
        "price_usd": price_usd,
        "timestamp": timestamp,
        "source": "Coindesk"
    }

# 2. Send data to Kinesis Stream
def send_to_kinesis(stream_name, region_name, data):
    """
    Send a single record (dict) to an AWS Kinesis Data Stream.

    Args:
        stream_name (str): Name of the Kinesis stream.
        region_name (str): AWS region (e.g., 'us-east-1').
        data (dict): Data to send.

    Returns:
        dict: Response from Kinesis put_record API.
    """
    kinesis_client = boto3.client('kinesis', region_name=region_name)

    partition_key = "partitionKey"  # Can be random or fixed

    response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=json.dumps(data),
        PartitionKey=partition_key
    )

    return response

# 3. Utility - Get current UTC time (optional, useful later)
def current_utc_time():
    """
    Get the current UTC timestamp in ISO format.

    Returns:
        str: Current UTC timestamp.
    """
    return datetime.utcnow().isoformat()
