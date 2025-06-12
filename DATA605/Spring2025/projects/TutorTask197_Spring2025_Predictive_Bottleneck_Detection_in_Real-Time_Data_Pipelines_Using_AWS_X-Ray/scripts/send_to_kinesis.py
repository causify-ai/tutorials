import json
import time
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from kinesis_client import create_kinesis_client
from fetch_bitcoin import fetch_bitcoin_price

# Create a Kinesis client
kinesis_client = create_kinesis_client()
stream_name = 'bitcoin-stream'  

def send_bitcoin_price_to_kinesis():
    """
    Fetch Bitcoin price and send it to Kinesis.
    """
    while True:
        try:
            price = fetch_bitcoin_price()
            timestamp = int(time.time())

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

            print(f"✅ Sent record: {record}")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(30)

if __name__ == "__main__":
    send_bitcoin_price_to_kinesis()
