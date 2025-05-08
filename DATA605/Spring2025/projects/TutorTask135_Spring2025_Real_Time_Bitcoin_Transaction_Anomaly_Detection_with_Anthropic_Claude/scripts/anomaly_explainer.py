import os
import boto3
import pyarrow.parquet as pq
import pyarrow.fs as pafs
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

S3_BUCKET = "btc-anomaly"
PROCESSED_PREFIX = "processed"

def get_latest_processed_folder(bucket, prefix):
    s3 = boto3.client("s3")
    result = s3.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/")
    folders = set()

    for obj in result.get("Contents", []):
        parts = obj["Key"].split("/")
        if len(parts) >= 4:
            folders.add(f"{parts[1]}/{parts[2]}/{parts[3]}")

    return sorted(folders)[-1] if folders else None

def explain(tx_data):
    prompt = f"""
    Analyze this Bitcoin transaction: {tx_data}

    Consider:
    - Deviation from account history patterns
    - Network-wide statistical baselines
    - Common attack signatures

    Then explain:
    - How it deviates from expected behavior
    - Why it may be considered anomalous
    - Summary explanation for financial analysts
    """

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content

def main():
    folder = get_latest_processed_folder(S3_BUCKET, PROCESSED_PREFIX)
    if not folder:
        print("No processed folder found.")
        return

    s3_path = f"s3://{S3_BUCKET}/{PROCESSED_PREFIX}/{folder}"
    fs, path = pafs.FileSystem.from_uri(s3_path)
    dataset = pq.ParquetDataset(path, filesystem=fs)
    table = dataset.read()
    df = table.to_pandas()

    if df.empty:
        print("No data found.")
        return

    sample = df.sample(min(3, len(df)))

    for idx, row in sample.iterrows():
        result = explain(row.to_dict())
        print(f"\nExplanation for transaction {idx}:\n{result}\n")

if __name__ == "__main__":
    main()