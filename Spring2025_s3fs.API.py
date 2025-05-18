import pandas as pd
import s3fs
from bitcoin_utils import fetch_bitcoin_data

# Set your API key
api_key = "CG-5pibUvyXCBs3EpUFkQg3nDoX"

# Fetch data using utility function
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
