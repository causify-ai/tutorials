import os
import json
import requests
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def fetch_90day_btc_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "90",
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["prices"]  # list of [timestamp, price]

def upload_bulk_to_s3(price_list):
    s3 = boto3.client('s3')
    bucket = os.getenv("S3_BUCKET")

    for ts_ms, price in price_list:
        timestamp = datetime.utcfromtimestamp(ts_ms / 1000).isoformat()
        data = {"timestamp": timestamp, "price": price}
        filename = f"btc_price_{timestamp}.json"

        try:
            s3.put_object(
                Bucket=bucket,
                Key=filename,
                Body=json.dumps(data)
            )
            print(f"✅ Uploaded: {filename}")
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")

if __name__ == "__main__":
    prices = fetch_90day_btc_history()
    upload_bulk_to_s3(prices)
