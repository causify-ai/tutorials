# fetch_bitcoin.py

from QlikAnalysis_utils import initialize_csv_file, fetch_bitcoin_price, append_to_csv
import time

CSV_PATH = "/Users/aj/Library/CloudStorage/Dropbox/Bitcoin_Analysis/bitcoin_realtime.csv"
FETCH_INTERVAL_SECONDS = 10

def main():
    initialize_csv_file(CSV_PATH)
    while True:
        record = fetch_bitcoin_price()
        if record:
            append_to_csv(record, CSV_PATH)
        time.sleep(FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
