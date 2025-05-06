# send_btc_to_kinesis.py

import time
from utils.utils import fetch_bitcoin_price, send_to_kinesis


STREAM_NAME = "bitcoin-price-stream"

def main():
    print(f" Starting BTC price streaming to Kinesis: {STREAM_NAME}")
    while True:
        try:
            btc_data = fetch_bitcoin_price()
            print(" Fetched:", btc_data)
            response = send_to_kinesis(STREAM_NAME, btc_data )
            print(" Sent to Kinesis | Sequence #: ", response["SequenceNumber"])
        except Exception as e:
            print(" Error:", e)
        time.sleep(10)

if __name__ == "__main__":
    main()
