# ingest/lambda_function.py

import os
import json
from utils.lambda_utils import get_live_btc_price, upload_to_s3

def lambda_handler(event, context):
    # Get bucket and prefix from environment variables
    bucket = os.environ.get('S3_BUCKET')
    prefix = os.environ.get('S3_PREFIX', '')

    # Fetch BTC price and upload to S3
    data = get_live_btc_price()
    s3_path = upload_to_s3(data, bucket, prefix)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'BTC price uploaded successfully',
            's3_uri': s3_path,
            'price': data
        })
    }
