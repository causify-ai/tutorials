# utils/utils.py

import boto3
import json
import requests
from datetime import datetime

# 1. Fetch real-time Bitcoin price
def fetch_bitcoin_price(
        api_url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_vol=true"):
    """
    Fetch the current Bitcoin price and 24hr volume in USD from CoinGecko.

    Args:
        api_url (str): CoinGecko API endpoint.

    Returns:
        dict: Bitcoin price and volume data with timestamp.
    """
    response = requests.get(api_url)
    data = response.json()

    price_usd = data["bitcoin"]["usd"]
    volume_usd = data["bitcoin"]["usd_24h_vol"]
    timestamp = datetime.utcnow().isoformat()

    return {
        "price_usd": price_usd,
        "volume_usd": volume_usd,
        "timestamp": timestamp,
        "source": "CoinGecko"
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
