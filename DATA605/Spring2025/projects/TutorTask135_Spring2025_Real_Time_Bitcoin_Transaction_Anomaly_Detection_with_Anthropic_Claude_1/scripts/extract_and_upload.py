import os
import json
import time
import requests
from datetime import datetime

# Config
BLOCKCHAIR_URL = "https://api.blockchair.com/bitcoin/transactions"
LOCAL_RAW_PATH = "../data/raw"
TXNS_PER_PAGE = 100
MAX_PAGES = 40  # ~4000 transactions max to stay under API limits
THROTTLE_SECONDS = 2.2  # To stay under 30 requests/minute

def fetch_transactions(offset: int):
    try:
        url = f"{BLOCKCHAIR_URL}?offset={offset}&limit={TXNS_PER_PAGE}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"[ERROR] {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None

def extract_features(tx_list):
    enriched = []
    for tx in tx_list:
        try:
            enriched.append({
                "timestamp": tx.get("time"),
                "tx_hash": tx.get("hash"),
                "block_id": tx.get("block_id"),
                "value": tx.get("output_total"),
                "value_usd": tx.get("output_total_usd"),
                "fee": tx.get("fee"),
                "fee_usd": tx.get("fee_usd"),
                "input_count": tx.get("input_count"),
                "output_count": tx.get("output_count"),
                "size": tx.get("size"),
                "fee_per_kb": tx.get("fee_per_kb"),
                "fee_per_kb_usd": tx.get("fee_per_kb_usd"),
                "fee_to_value_ratio": round((tx["fee"] / tx["output_total"]), 6)
                    if tx.get("fee") and tx.get("output_total") and tx["output_total"] > 0 else None
            })
        except Exception as e:
            print(f"[WARN] Skipping transaction due to error: {e}")
    return enriched

def save_locally(data, filename):
    os.makedirs(LOCAL_RAW_PATH, exist_ok=True)
    path = os.path.join(LOCAL_RAW_PATH, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def main():
    print("[INFO] Starting extraction for today (latest transactions)...")

    page = 0
    total_txns = 0
    while page < MAX_PAGES:
        offset = page * TXNS_PER_PAGE
        print(f"[INFO] Fetching offset {offset}...")

        tx_data = fetch_transactions(offset)
        if tx_data is None:
            break
        if not tx_data:
            print("[INFO] No more data returned. Stopping early.")
            break

        enriched = extract_features(tx_data)
        now = datetime.utcnow()
        filename = f"batch_{now.strftime('%Y%m%d_%H%M%S')}_page{page}.json"
        save_locally(enriched, filename)
        print(f"[INFO] Saved: {filename}")

        total_txns += len(enriched)
        page += 1

        if page < MAX_PAGES:
            time.sleep(THROTTLE_SECONDS)

    print(f"[INFO] Total transactions extracted: {total_txns}")
    print("[INFO] Daily extraction completed.")
    print("Data extraction completed successfully.")

if __name__ == "__main__":
    main()