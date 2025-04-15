import time
from fetch_full_data import fetch_btc_data_dict
from serialize_data import save_to_daily_file

print("🔁 Starting real-time BTC collector (every 30s)")

try:
    while True:
        data = fetch_btc_data_dict()
        if data:
            save_to_daily_file(data)
        else:
            print("⚠️ Skipped due to API error")
        time.sleep(30)
except KeyboardInterrupt:
    print("⏹️ Stopped.")