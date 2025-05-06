import os
import json
import time
import requests
import boto3
from datetime import datetime

# CONFIGURATION
BLOCKCHAIR_URL = "https://api.blockchair.com/bitcoin/transactions?limit=500"
LOCAL_SAVE_PATH = "data_batches"
S3_BUCKET = "btc-anomaly"  # Change this if needed
S3_FOLDER = "raw"
INTERVAL_SECONDS = 1800  # # every 30 minutes. To stay well under limits
NUM_BATCHES = 3        # You can increase for more

# AWS S3 Setup
s3 = boto3.client("s3")

def fetch_transactions():
    try:
        response = requests.get(BLOCKCHAIR_URL)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"Blockchair error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print("Exception during fetch:", e)
        return []

def save_locally(data, filename):
    os.makedirs(LOCAL_SAVE_PATH, exist_ok=True)
    path = os.path.join(LOCAL_SAVE_PATH, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def upload_to_s3(local_path, s3_key):
    try:
        s3.upload_file(local_path, S3_BUCKET, s3_key)
        print(f"Uploaded to S3: s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print("S3 upload failed:", e)

def run_extraction_loop(batches=NUM_BATCHES):
    for i in range(batches):
        print(f"Batch {i+1}")
        data = fetch_transactions()
        if not data:
            print("No data fetched.")
            time.sleep(INTERVAL_SECONDS)
            continue

        now = datetime.utcnow()
        filename = f"batch_{now.strftime('%Y%m%d_%H%M%S')}.json"
        s3_key = f"{S3_FOLDER}/{now.strftime('%Y/%m/%d')}/{filename}"

        local_path = save_locally(data, filename)
        upload_to_s3(local_path, s3_key)
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    run_extraction_loop()