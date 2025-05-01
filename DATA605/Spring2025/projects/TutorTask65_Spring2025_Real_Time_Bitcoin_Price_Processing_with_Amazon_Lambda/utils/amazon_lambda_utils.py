import requests
import datetime
import json
import boto3

def get_live_btc_price():
    """
    Simulate a Lambda function that fetches live Bitcoin price.
    """

    url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        price = data['data']['amount']
        timestamp = datetime.datetime.utcnow().isoformat()

        result = {
            'price': float(price),
            'timestamp': timestamp
        }
        return result
    else:
        raise Exception(f"Failed to fetch BTC price. Status Code: {response.status_code}")

def upload_to_s3(data, bucket_name, file_name):
    """
    Simulate a Lambda function that uploads data to S3.
    """

    # Create S3 client
    s3 = boto3.client('s3',region_name='us-east-1')

    # Convert data to JSON string
    json_data = json.dumps(data)

    # Upload JSON to S3 bucket
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json_data)

    return f"s3://{bucket_name}/{file_name}"
