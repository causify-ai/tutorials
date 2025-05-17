import os
import json
import time
import requests
from datetime import datetime, timedelta

# Parameters
OUTPUT_DIR = "data/raw"
LIMIT_PER_PAGE = 100
MAX_PAGES = 100  # To prevent infinite requests (adjust based on credits)
DELAY_BETWEEN_REQUESTS = 2  # To avoid hitting 30 requests/min API limit

def fetch_page(offset):
    url = f"https://api.blockchair.com/bitcoin/transactions?limit={LIMIT_PER_PAGE}&offset={offset}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"[ERROR] {response.status_code}: {response.text}")
        return []

def filter_by_date(transactions, target_date_str):
    filtered = []
    for tx in transactions:
        tx_time = tx.get("time")
        if not tx_time:
            continue
        tx_dt = datetime.strptime(tx_time, "%Y-%m-%d %H:%M:%S")
        if tx_dt.strftime("%Y-%m-%d") == target_date_str:
            filtered.append(tx)
    return filtered

def run_extraction_for_date(target_date):
    print(f"[INFO] Starting extraction for date: {target_date}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total_saved = 0

    for page in range(MAX_PAGES):
        offset = page * LIMIT_PER_PAGE
        print(f"[INFO] Fetching offset {offset}...")

        txs = fetch_page(offset)
        if not txs:
            print("[INFO] No more data returned. Stopping early.")
            break

        filtered = filter_by_date(txs, target_date)

        if not filtered:
            print("[INFO] No matching transactions in this page. Stopping early.")
            break

        filename = f"batch_{target_date.replace('-', '')}_page{page}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(filtered, f, indent=2)
        print(f"[INFO] Saved: {filename}")
        total_saved += len(filtered)

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"[INFO] Total transactions extracted for {target_date}: {total_saved}")
    print("[INFO] Daily extraction completed.")

if __name__ == "__main__":
    # Example: extract 2025-05-10
    run_extraction_for_date("2025-05-10")