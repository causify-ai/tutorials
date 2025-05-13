# stream_loop.py

import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bitcoin_utils import fetch_btc_data_dict, save_to_daily_file

print("🚀 Starting real-time Bitcoin data collection (every 30 seconds)...")

try:
    while True:
        print("📡 Fetching live data...")
        data = fetch_btc_data_dict()
        save_to_daily_file(data)
        print(f"✅ Saved at {datetime.now().ctime()}")
        time.sleep(30)

except KeyboardInterrupt:
    print("🛑 Stream interrupted by user. Exiting...")