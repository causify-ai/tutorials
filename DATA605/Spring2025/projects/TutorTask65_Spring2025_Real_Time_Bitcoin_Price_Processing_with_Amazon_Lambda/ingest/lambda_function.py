import sys
import os
import time
from datetime import datetime, timedelta, timezone

# Ensure utils folder is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.amazon_lambda_utils import get_live_btc_price, upload_to_s3

# S3 configuration
bucket_name = "ruthvick-btc-bucket"
key_prefix = "btc_data/btc_price_"

# Duration to run the loop (in seconds)
duration_limit = 2 * 60  # 2 minutes
end_time = datetime.now(timezone.utc) + timedelta(seconds=duration_limit)

print(f"Running scheduled fetch for {duration_limit} seconds...")

while datetime.now(timezone.utc) < end_time:
    btc_data = get_live_btc_price()
    print(f"Fetched BTC Price: {btc_data}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    key = f"{key_prefix}{timestamp}.json"

    upload_to_s3(btc_data, bucket_name, key)
    print(f"Data uploaded to s3://{bucket_name}/{key}\n")

    time.sleep(15)

print("Scheduled fetch completed.")
