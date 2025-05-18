# utils/lambda_utils.py

import json
import datetime
from urllib.request import urlopen
import boto3

def get_live_btc_price():
    """
    Fetch current BTC-USD spot price from Coinbase.
    Returns a dict with timestamp and price.
    """
    url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    with urlopen(url) as response:
        data = json.loads(response.read().decode())
        price = float(data['data']['amount'])
        timestamp = datetime.datetime.utcnow().isoformat()
    return {'timestamp': timestamp, 'price': price}

def upload_to_s3(data, bucket, prefix):
    """
    Uploads the given data to S3 as a JSON file with a timestamped filename.
    """
    filename = f"{prefix}btc_price_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket,
        Key=filename,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    return f"s3://{bucket}/{filename}"
