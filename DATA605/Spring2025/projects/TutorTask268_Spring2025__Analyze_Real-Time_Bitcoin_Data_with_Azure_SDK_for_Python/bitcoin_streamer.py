from azure.identity import ClientSecretCredential
from azure.eventhub import EventHubProducerClient, EventData
import requests
import json
import time

#latest version of code..

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Azure Authentication
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Event Hub details
EVENT_HUB_NAMESPACE = os.getenv("EVENT_HUB_NAMESPACE")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")


# Authenticate
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

producer = EventHubProducerClient(
    fully_qualified_namespace=EVENT_HUB_NAMESPACE,
    eventhub_name=EVENT_HUB_NAME,
    credential=credential
)

# Function to fetch Bitcoin price
def fetch_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Safe checking
        if isinstance(data, dict) and 'bitcoin' in data:
            bitcoin_info = data['bitcoin']
            if isinstance(bitcoin_info, dict) and 'usd' in bitcoin_info:
                price = bitcoin_info['usd']
                if isinstance(price, (int, float)):
                    return price

        print(f"⚠️ Invalid API response structure: {data}")
        return None

    except Exception as e:
        print(f"⚠️ Fetch exception: {repr(e)}")
        return None

# Main loop
try:
    while True:
        try:
            price = fetch_bitcoin_price()

            if price is not None:
                try:
                    message = {
                        "currency": "BTC",
                        "price_usd": float(price),
                        "timestamp": time.time()
                    }

                    event_data_batch = producer.create_batch()
                    event_data_batch.add(EventData(json.dumps(message)))
                    producer.send_batch(event_data_batch)

                    print(f"✅ Sent: {message}")

                except Exception as e:
                    print(f"⚠️ Error sending event: {repr(e)}")
            else:
                print("⚠️ Skipped sending due to invalid price.")

            time.sleep(60)

        except Exception as e:
            print(f"⚠️ Unexpected error inside loop: {repr(e)}")
            time.sleep(5)

except KeyboardInterrupt:
    print("❗ Script stopped manually.")

finally:
    producer.close()