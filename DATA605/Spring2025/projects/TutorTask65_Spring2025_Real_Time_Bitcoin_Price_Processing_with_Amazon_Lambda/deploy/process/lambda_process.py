import os
import json
import datetime
import boto3
from lambda_utils_process import list_recent_btc_prices

def lambda_handler(event, context):
    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ["S3_PREFIX"]
    limit = int(os.environ.get("PROCESS_LIMIT", 10))  # Number of recent files to analyze

    try:
        # Step 1: Read recent BTC prices
        prices_data = list_recent_btc_prices(bucket, prefix, limit)

        if not prices_data:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "No BTC price data available in S3.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })
            }

        # Step 2: Compute stats
        avg_price = round(sum(p["price_usd_per_btc"] for p in prices_data) / len(prices_data), 2)
        result = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "count": len(prices_data),
            "average_price_usd": avg_price,
            "latest_timestamp": prices_data[0]["timestamp"],
            "oldest_timestamp": prices_data[-1]["timestamp"]
        }

        # Step 3: Save result to S3
        now = datetime.datetime.utcnow()
        summary_key = f"processed/summary_{now.strftime('%Y%m%dT%H%M%S')}.json"
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=bucket,
            Key=summary_key,
            Body=json.dumps(result),
            ContentType="application/json"
        )
        print(f"[DEBUG] Summary uploaded to: s3://{bucket}/{summary_key}")

        # Step 4: Return result
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        }
