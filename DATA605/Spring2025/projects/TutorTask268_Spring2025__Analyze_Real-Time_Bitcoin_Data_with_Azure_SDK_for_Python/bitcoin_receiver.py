import asyncio
import json
import logging
import os
from typing import Any, Dict

from azure.eventhub.aio import EventHubConsumerClient
from azure.storage.blob.aio import BlobServiceClient
from dotenv import load_dotenv

from bitcoin_utils import get_azure_async_credential, upload_buffer_to_blob

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Environment
STORAGE_ACCOUNT_URL = os.getenv("STORAGE_ACCOUNT_URL")
STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME")
EVENT_HUB_NAMESPACE = os.getenv("EVENT_HUB_NAMESPACE")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")

# Shared buffer
events_buffer: list[Dict[str, Any]] = []


async def handle_event(partition_context: Any, event: Any) -> None:
    """
    Callback triggered on receiving each Event Hub message.
    """
    try:
        event_data = json.loads(event.body_as_str())
        events_buffer.append(event_data)
        logger.info("Received: %s", event_data)
    except Exception as error:
        logger.error("Failed to process event: %s", repr(error))


async def receive_bitcoin_data() -> None:
    """
    Listens to Event Hub and uploads batches of data to Azure Blob Storage.
    """
    credential = get_azure_async_credential()

    consumer = EventHubConsumerClient(
        fully_qualified_namespace=EVENT_HUB_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        consumer_group=CONSUMER_GROUP,
        credential=credential
    )

    blob_service = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

    async with consumer:
        logger.info("Listening for new events...")
        asyncio.create_task(
            consumer.receive(
                on_event=handle_event,
                starting_position="@latest",
                prefetch=10
            )
        )

        while True:
            await asyncio.sleep(10)
            if len(events_buffer) >= 50:  # Test threshold
                await upload_buffer_to_blob(blob_service, STORAGE_CONTAINER_NAME, events_buffer)
                events_buffer.clear()


def main() -> None:
    try:
        asyncio.run(receive_bitcoin_data())
    except KeyboardInterrupt:
        logger.info("Receiver stopped manually.")
    except Exception as error:
        logger.exception("Fatal receiver error: %s", repr(error))


if __name__ == "__main__":
    main()
