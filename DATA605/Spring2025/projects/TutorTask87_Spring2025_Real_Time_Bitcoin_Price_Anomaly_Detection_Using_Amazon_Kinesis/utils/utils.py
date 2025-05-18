# utils/utils.py

import boto3
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import joblib
import numpy as np


model_path = os.path.join(os.path.dirname(__file__), "isolation_forest_model.pkl")
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
#print(model_path)
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
# Load environment variables from .env file
load_dotenv()

# boto3 will now automatically use these
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_DEFAULT_REGION")


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
def send_to_kinesis(stream_name, data):
    """
    Send a single record (dict) to an AWS Kinesis Data Stream.

    Args:
        stream_name (str): Name of the Kinesis stream.
        region_name (str): AWS region (e.g., 'us-east-1').
        data (dict): Data to send.

    Returns:
        dict: Response from Kinesis put_record API.
    """
    kinesis_client = boto3.client('kinesis')

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

def send_to_firehose_raw(data):
    firehose = boto3.client('firehose', region_name='us-east-1')
    written_raw = firehose.put_record(
        DeliveryStreamName='btc-firehose-raw',
        Record={'Data': json.dumps(data) + '\n'}
    )
    return written_raw



def send_to_kinesis_processed(data):
    # Send processed to new Kinesis stream
    kinesis = boto3.client('kinesis')

    partition_key = "partitionKey"
    written_processed = kinesis.put_record(
        StreamName="btc-processed-stream",
        Data=json.dumps(data),
        PartitionKey=partition_key
    )
    return written_processed



def send_anomaly():
    kinesis_client = boto3.client('kinesis')
    data = {
        "price": 9999999.0,  # way outside normal range
        "volume": 9999.0,
        "timestamp": current_utc_time()
    }
    anomaly = kinesis_client.put_record(
        StreamName="bitcoin-price-stream",
        Data=json.dumps(data),
        PartitionKey="test"
    )
    return anomaly,data

def detect_anomaly(data):
    price = data.get("price")
    volume = data.get("volume")
    timestamp = data.get("timestamp")
    features = np.array([[price, volume]])
    scaled = scaler.transform(features)

    score = model.decision_function(scaled)[0]
    score = model.predict(scaled)

    if score[0]==-1:
        is_anomaly = True
    else:
        is_anomaly = False

    return {
        "price": price,
        "volume": volume,
        "timestamp": timestamp,
        "anomaly_score": int(score[0]),
        "is_anomaly": is_anomaly
    }