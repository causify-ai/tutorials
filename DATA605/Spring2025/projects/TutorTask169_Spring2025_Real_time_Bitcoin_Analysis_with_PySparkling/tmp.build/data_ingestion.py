import os
import time
import pandas as pd
from datetime import datetime
import requests

# ── Real Streaming Bitcoin Price Data ────────────────────────────────
DATA_DIR = "/root/bitcoin_project/data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "stream_data.csv")

# Initialize CSV if it doesn't exist
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=["timestamp", "price"]).to_csv(CSV_PATH, index=False)

# Parameters for rate-limit backoff
base_sleep = 10           # seconds between successful calls
backoff_sleep = base_sleep
max_backoff = 600         # don't exceed 10 minutes on backoff

while True:
    ts = int(time.time())
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=5
        )
        if resp.status_code == 429:
            print(f"{datetime.utcnow().isoformat()}  429 Rate limit hit, sleeping for {backoff_sleep}s")
            time.sleep(backoff_sleep)
            backoff_sleep = min(backoff_sleep * 2, max_backoff)
            continue

        resp.raise_for_status()
        price = resp.json()["bitcoin"]["usd"]
        backoff_sleep = base_sleep  # reset backoff after success

    except Exception as e:
        print(f"{datetime.utcnow().isoformat()}  Error fetching price: {e}")
        time.sleep(base_sleep)
        continue

    # Append to CSV
    pd.DataFrame([{"timestamp": ts, "price": price}]) \
        .to_csv(CSV_PATH, mode="a", header=False, index=False)

    print(f"{datetime.utcnow().isoformat()}  Ingested price={price} at timestamp={ts}")
    time.sleep(base_sleep)
