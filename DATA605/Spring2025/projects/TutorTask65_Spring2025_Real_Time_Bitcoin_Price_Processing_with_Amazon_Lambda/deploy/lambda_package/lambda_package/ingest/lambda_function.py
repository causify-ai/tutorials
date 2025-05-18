import os
from utils.lambda_utils import process_and_upload

def lambda_handler(event, context):
    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ["S3_PREFIX"]
    result = process_and_upload(bucket, prefix)
    return {
        "statusCode": 200,
        "body": result
    }
