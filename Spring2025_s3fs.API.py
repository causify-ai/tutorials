import pandas as pd
import s3fs
import os
from bitcoin_utils import fetch_bitcoin_data

# Set API key from environment variable
api_key = os.getenv("COINGECKO_API_KEY")

if not api_key:
    raise ValueError("COINGECKO_API_KEY not set in environment variables.")

# Fetch data
df = fetch_bitcoin_data(api_key=api_key, days=365)

# Save locally
df.to_csv("bitcoin_prices.csv", index=False)

# Upload to S3
try:
    fs = s3fs.S3FileSystem(anon=False)
    with fs.open("bitcoin-timeseries-data-kv/bitcoin_prices.csv", "w") as f:
        df.to_csv(f, index=False)
    print("Upload to S3 successful.")
except Exception as e:
    print(f"S3 upload failed: {e}")
