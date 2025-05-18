import json
import time
import sys
import os
from datetime import datetime

from utils.kinesis_client import create_kinesis_client
from utils.fetch_bitcoin import fetch_current_bitcoin_price, get_bitcoin_price_history_hourly_chunks

# Create a Kinesis client
kinesis_client = create_kinesis_client()
stream_name = 'bitcoin-stream'  


def send_historical_bitcoin_prices_to_kinesis(batch_size=400):
    """
    Fetch historical hourly Bitcoin prices and send to Kinesis in batches.
    """
    prices = get_bitcoin_price_history_hourly_chunks()
    print(f"📊 Total records fetched: {len(prices)}")

    records_batch = []

    now_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    if prices and datetime.fromtimestamp(prices[-1][0] / 1000).replace(minute=0, second=0, microsecond=0) == now_hour:
        prices = prices[:-1]  # drop last duplicate hour

    for ts, price in prices:
        try:
            # Round timestamp to hour
            dt = datetime.fromtimestamp(ts / 1000)
            dt_hour = dt.replace(minute=0, second=0, microsecond=0)
            timestamp = int(dt_hour.timestamp())

            record = {
                'asset': 'bitcoin',
                'price_usd': price,
                'timestamp': timestamp
            }

            # Format for Kinesis batch
            records_batch.append({
                'Data': json.dumps(record),
                'PartitionKey': 'bitcoin'
            })

            # Send batch if full
            if len(records_batch) == batch_size:
                response = kinesis_client.put_records(
                    Records=records_batch,
                    StreamName=stream_name
                )
                print(f"✅ Sent batch of {len(records_batch)} records")
                records_batch = []
                time.sleep(1)  # polite delay between batches

        except Exception as e:
            print(f"❌ Error preparing record: {e}")

    # Send any leftover records
    if records_batch:
        kinesis_client.put_records(
            Records=records_batch,
            StreamName=stream_name
        )
        print(f"✅ Sent final batch of {len(records_batch)} records")

def send_current_bitcoin_price_to_kinesis():
    """
    Fetch Bitcoin price every hour and send it to Kinesis,
    using a timestamp floored to the hour.
    """
    while True:
        try:
            price = fetch_current_bitcoin_price()

            dt = datetime.now().replace(minute=0, second=0, microsecond=0)
            timestamp = int(dt.timestamp())

            record = {
                'asset': 'bitcoin',
                'price_usd': price,
                'timestamp': timestamp
            }

            kinesis_client.put_record( 
                StreamName=stream_name,
                Data=json.dumps(record),
                PartitionKey='bitcoin'
            )

            print(f"✅ Sent record for {dt}: ${price}")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(3600)  # wait until next hour

# if __name__ == "__main__":
#     send_historical_bitcoin_prices_to_kinesis()
#     send_current_bitcoin_price_to_kinesis()
