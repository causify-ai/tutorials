import asyncio
import json
import time
from azure.identity.aio import ClientSecretCredential
from azure.eventhub.aio import EventHubConsumerClient
from azure.storage.blob.aio import BlobServiceClient

# Azure Authentication Details
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
STORAGE_ACCOUNT_URL = os.getenv("STORAGE_ACCOUNT_URL")
STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME")
EVENT_HUB_NAMESPACE = os.getenv("EVENT_HUB_NAMESPACE")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")


# Memory buffer for events
events_buffer = []

# Connect Azure credentials
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# Function to upload buffer to Blob Storage
async def upload_to_blob(blob_service_client):
    filename = f"bitcoin_data_{int(time.time())}.json"
    data_to_upload = json.dumps(events_buffer, indent=2)
    
    blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=filename)
    await blob_client.upload_blob(data_to_upload, overwrite=True)
    
    print(f"✅ Uploaded {len(events_buffer)} events to Blob Storage as {filename}")

# Callback to process incoming events
async def on_event(partition_context, event):
    event_data = json.loads(event.body_as_str())
    print(f"📩 Received event: {event_data}")
    events_buffer.append(event_data)

# Main function to run receiver
async def main():
    client = EventHubConsumerClient(
        fully_qualified_namespace=EVENT_HUB_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        consumer_group=CONSUMER_GROUP,
        credential=credential,
    )

    blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

    async with client:
        print("📡 Listening for events...") 
        receive_task = asyncio.create_task(
            client.receive(
                on_event=on_event,
                starting_position="@latest",  # Start from beginning of stream
                prefetch=10  # Fetch a few events at once (small optimization)
            )
        )

        while True:
            await asyncio.sleep(10)  # Check every 10 seconds
            if len(events_buffer) >= 50:  # Only upload when 100 events collected
                await upload_to_blob(blob_service_client)
                events_buffer.clear()

# Run
if __name__ == '__main__':
    asyncio.run(main())
