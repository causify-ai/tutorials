# bitcoin_data_ingestion.py

import time
from bitcoin_utils import fetch_and_store

def main():
    """
    Continuously fetch Bitcoin price data every 60 seconds
    and append to bitcoin_price_data.csv
    """
    print("Starting real-time ingestion (Ctrl-C to stop)...")
    try:
        while True:
            fetch_and_store()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nIngestion stopped by user.")

if __name__ == "__main__":
    main()
