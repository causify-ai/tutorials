# bitcoin_producer.py

from bitcoin_emr_utils import fetch_bitcoin_price, save_price_to_s3
import time

bucket = 'bitcoin-price-streaming-data'
folder = 'data_v2'

while True:
    try:
        price = fetch_bitcoin_price()
        save_price_to_s3(bucket=bucket, folder=folder, price_usd=price)
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(60)  # wait 1 minute

