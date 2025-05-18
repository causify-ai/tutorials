import pandas as pd
import s3fs
import json
from io import StringIO

def load_all_btc_data():
    fs = s3fs.S3FileSystem(anon=False)

    # List all JSON files in the S3 path
    files = fs.ls('bitcoin-timeseries-data-kv/bitcoin/')
    json_files = [f for f in files if f.endswith('.json')]

    if not json_files:
        raise ValueError("No JSON files found in S3 bucket.")

    # Sort files by timestamp in filename (descending)
    latest_file = sorted(json_files, reverse=True)[0]
    print("📂 Loading from:", latest_file)

    # Read JSON content from S3
    with fs.open(latest_file, 'r') as f:
        raw_json = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(raw_json)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df = df.sort_index()

    print("✅ Parsed DataFrame shape:", df.shape)
    return df
