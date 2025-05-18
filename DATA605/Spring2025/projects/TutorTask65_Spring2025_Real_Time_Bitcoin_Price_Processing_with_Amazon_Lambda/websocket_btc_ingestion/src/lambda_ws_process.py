import os
import json
import boto3
import datetime

def lambda_handler(event, context):
    s3 = boto3.client("s3")
    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ["S3_PREFIX"]

    result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    files = sorted(result.get("Contents", []), key=lambda x: x["LastModified"], reverse=True)[:10]

    records = []
    for obj in files:
        data = s3.get_object(Bucket=bucket, Key=obj["Key"])
        body = data["Body"].read()
        if not body.strip():
            continue
        parsed = json.loads(body)
        records.append(parsed)

    if not records:
        return {"statusCode": 200, "body": "No data found"}

    avg_price = round(sum(r["price_usd_per_btc"] for r in records) / len(records), 2)
    summary = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "average_price_usd": avg_price,
        "count": len(records),
        "latest_timestamp": records[0]["timestamp"],
        "oldest_timestamp": records[-1]["timestamp"]
    }

    key = f"websocket_processed/summary_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(summary), ContentType="application/json")

    return {
        "statusCode": 200,
        "body": json.dumps(summary)
    }
