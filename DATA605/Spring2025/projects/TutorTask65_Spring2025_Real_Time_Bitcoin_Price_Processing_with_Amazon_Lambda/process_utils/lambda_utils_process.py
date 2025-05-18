import json
import boto3

def list_recent_btc_prices(bucket, prefix, limit=10):
    """
    List the most recent BTC price files from S3 and return parsed JSON data.
    """
    s3 = boto3.client("s3")
    result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if "Contents" not in result:
        return []

    files = sorted(result["Contents"], key=lambda x: x["LastModified"], reverse=True)[:limit]

    prices = []
    for obj in files:
        try:
            response = s3.get_object(Bucket=bucket, Key=obj["Key"])
            content = response["Body"].read()
            data = json.loads(content)

            if "price_usd_per_btc" in data:
                prices.append(data)
        except Exception as e:
            print(f"[WARN] Could not read {obj['Key']}: {str(e)}")
            continue

    return prices
