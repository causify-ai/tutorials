import os
import json
import pandas as pd
import anthropic
import boto3
import pyarrow.parquet as pq
import s3fs
from datetime import datetime

# CONFIG
S3_INPUT_PARQUET = "s3://btc-anomaly/processed/2025/04/21/output_*.parquet"
S3_OUTPUT_PATH = "s3://btc-anomaly/explained/2025/04/21/explained_batch_{}.json".format(
    datetime.utcnow().strftime("%H%M%S")
)
LOCAL_OUTPUT_FILE = "explained_batch.json"
MAX_EXPLANATIONS = 5

# Claude setup
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Read from S3
fs = s3fs.S3FileSystem()
files = fs.glob(S3_INPUT_PARQUET.replace("s3://", ""))

dataframes = []
for file in files:
    with fs.open(file, 'rb') as f:
        table = pq.read_table(f)
        df = table.to_pandas()
        dataframes.append(df)

df_all = pd.concat(dataframes)
df_anomalous = df_all[df_all["is_anomalous"] == 1]
df_sample = df_anomalous.sample(n=min(len(df_anomalous), MAX_EXPLANATIONS))

def explain_transaction(row):
    tx_data = row.to_dict()
    tx_json = json.dumps(tx_data, indent=2)
    prompt = f"""
Analyze this Bitcoin transaction:
{tx_json}

Consider:
- Deviation from the address’s historical patterns (volume, fees, flow)
- Deviation from network-wide statistical norms
- Known suspicious transaction signatures or attack patterns

Also explain:
- How it deviates from expected behavior
- Why it may be considered anomalous
- Summary explanation for financial analysts
"""
    try:
        response = client.messages.create(
            model="claude-2.1",
            max_tokens=300,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0]["text"]
    except Exception as e:
        return f"Error calling Claude: {str(e)}"

df_sample["explanation"] = df_sample.apply(explain_transaction, axis=1)
df_sample.to_json(LOCAL_OUTPUT_FILE, orient="records", indent=2)

s3 = boto3.client("s3")
s3.upload_file(LOCAL_OUTPUT_FILE, "btc-anomaly", f"explained/2025/04/21/{LOCAL_OUTPUT_FILE}")

print("Explanations uploaded to S3.")