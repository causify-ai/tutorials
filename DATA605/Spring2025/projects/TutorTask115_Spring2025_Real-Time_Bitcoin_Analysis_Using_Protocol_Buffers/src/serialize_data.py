import os
from datetime import datetime
import bitcoin_full_pb2

def save_to_daily_file(data_dict):
    msg = bitcoin_full_pb2.BitcoinFullData()
    for k, v in data_dict.items():
        setattr(msg, k, v)

    today = datetime.now().strftime("%Y-%m-%d")
    file_path = f"src/data/bitcoin_data_{today}.pb"
    os.makedirs("src/data", exist_ok=True)

    serialized = msg.SerializeToString()
    with open(file_path, "ab") as f:
        f.write(len(serialized).to_bytes(4, byteorder="little"))
        f.write(serialized)

    print(f"✅ Saved: {file_path}")