# send_btc_to_kinesis.py

import time

from src.tutorials1.DATA605.Spring2025.projects.TutorTask87_Spring2025_Real_Time_Bitcoin_Price_Anomaly_Detection_Using_Amazon_Kinesis.utils.utils import \
    send_to_kinesis_processed
from utils.utils import fetch_bitcoin_price, send_to_kinesis, send_to_firehose_raw, send_anomaly, detect_anomaly, send_to_kinesis_processed


STREAM_NAME = "bitcoin-price-stream"

def main():
    print(f" Starting BTC price streaming to Kinesis: {STREAM_NAME}")
    while True:
        try:
            btc_data = fetch_bitcoin_price()
            print(" Fetched:", btc_data)
            response = send_to_kinesis(STREAM_NAME, btc_data )
            print(" Sent to Kinesis | Sequence #: ", response["SequenceNumber"])
            written_raw = send_to_firehose_raw(btc_data)
            #print(written_raw)
            mapped = {
                    "price": btc_data["price_usd"],
                    "volume": btc_data["volume_usd"],
                    "timestamp": btc_data["timestamp"]
                }
            processed_btc= detect_anomaly(mapped)
            print(processed_btc)
            processed_sent_btc = send_to_kinesis_processed(processed_btc)
            #print(processed_sent_btc)
            anomaly,anomaly_data = send_anomaly()
            print(" Anomaly Sent to Kinesis | Sequence #: ", anomaly["SequenceNumber"])
            # Detect anomaly
            processed = detect_anomaly(anomaly_data)
            print(processed)
            processed_sent_anomaly = send_to_kinesis_processed(processed)
            #print(processed_sent_anomaly)
        except Exception as e:
            print(" Error:", e)
        time.sleep(15)

if __name__ == "__main__":
    main()
