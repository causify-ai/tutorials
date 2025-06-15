# realtime_ingestor.py

import time
from template_utils import insert_bitcoin_price

def run_ingestion_loop(interval_seconds=60):
    """
    Continuously fetch and insert BTC price every N seconds.
    :param interval_seconds: Delay between inserts (in seconds)
    """
    print(f"Starting real-time BTC ingestion (interval: {interval_seconds}s)...\nPress Ctrl+C to stop.")
    while True:
        try:
            insert_bitcoin_price()
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nIngestion loop stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    run_ingestion_loop(interval_seconds=60)
