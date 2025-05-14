# src/stream_loop.py

import os
import time
import datetime
from bitcoin_utils import fetch_btc_data_dict, dict_to_protobuf, save_to_length_delimited_file

def run_stream_loop(interval_sec=30):
    print("🚀 Starting real-time Bitcoin data collection (every 30 seconds)...")
    while True:
        try:
            # Fetch latest Bitcoin data
            data_dict = fetch_btc_data_dict()

            # Convert to protobuf object
            proto_obj = dict_to_protobuf(data_dict)

            # Save to daily .pb file (length-delimited)
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(script_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, f"bitcoin_data_{today_str}.pb")
            save_to_length_delimited_file(proto_obj, file_path)

            # Log
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"✅ [{timestamp}] Saved latest data to {file_path}")
        except Exception as e:
            print(f"❌ Error fetching or saving data: {e}")

        time.sleep(interval_sec)

if __name__ == "__main__":
    run_stream_loop()