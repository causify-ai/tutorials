import os
import time
import pandas as pd
from datetime import datetime
import random

# ── Simulate Streaming Bitcoin Price Data ────────────────────────────────
data_dir = "/root/bitcoin_project/data"
os.makedirs(data_dir, exist_ok=True)
csv_file_path = os.path.join(data_dir, "stream_data.csv")

if not os.path.exists(csv_file_path):
    df = pd.DataFrame(columns=["timestamp", "price"])
    df.to_csv(csv_file_path, index=False)

while True:
    timestamp = int(time.time())
    price = random.randint(30000, 60000)
    df = pd.DataFrame([{"timestamp": timestamp, "price": price}])
    df.to_csv(csv_file_path, mode="a", header=False, index=False)
    print(f"{datetime.utcnow().isoformat()}  Ingested price={price} at timestamp={timestamp}")
    time.sleep(10)
