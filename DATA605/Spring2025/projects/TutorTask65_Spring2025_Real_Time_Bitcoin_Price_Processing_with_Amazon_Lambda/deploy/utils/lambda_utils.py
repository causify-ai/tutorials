import json
import datetime
import boto3
import requests

def get_live_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    price = float(data["bitcoin"]["usd"])
    timestamp = datetime.datetime.utcnow().isoformat()
    return {"timestamp": timestamp, "price_usd_per_btc": price}

def get_last_price_from_s3(bucket, prefix):
    s3 = boto3.client("s3")
    result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    files = sorted(result.get("Contents", []), key=lambda x: x["LastModified"], reverse=True)

    if not files:
        return None

    for obj in files:
        try:
            last_obj = s3.get_object(Bucket=bucket, Key=obj["Key"])
            body = last_obj["Body"].read()
            if not body.strip():
                print(f"[WARN] Empty file: {obj['Key']}")
                continue  # Skip empty files
            last_data = json.loads(body)
            return last_data.get("price_usd_per_btc", None)
        except Exception as e:
            print(f"[ERROR] Skipping corrupted file {obj['Key']} — {e}")
            continue  # Try the next recent file

    return None  # If all files failed

def upload_to_s3(data, bucket, prefix):
    now = datetime.datetime.utcnow()
    key = f"{prefix}btc_price_{now.strftime('%Y%m%dT%H%M%S')}.json"
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    print(f"[DEBUG] Uploaded to: s3://{bucket}/{key}")
    return key

def process_and_upload(bucket, prefix):
    current = get_live_btc_price()
    last_price = get_last_price_from_s3(bucket, prefix)

    if last_price is not None:
        pct_change = ((current["price_usd_per_btc"] - last_price) / last_price) * 100
        current["pct_change"] = round(pct_change, 4)
    else:
        current["pct_change"] = None  # First data point

    upload_to_s3(current, bucket, prefix)
    return current
