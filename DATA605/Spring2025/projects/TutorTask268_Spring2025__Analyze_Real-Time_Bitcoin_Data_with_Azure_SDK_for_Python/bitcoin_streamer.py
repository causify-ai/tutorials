import json
import logging
import os
import time

from azure.eventhub import EventData, EventHubProducerClient
from dotenv import load_dotenv

from bitcoin_utils import get_azure_sync_credential, fetch_bitcoin_price_usd

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Environment
EVENT_HUB_NAMESPACE = os.getenv("EVENT_HUB_NAMESPACE")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")


def stream_bitcoin_data() -> None:
    """
    Streams live Bitcoin prices to Azure Event Hub at 60-second intervals.
    """
    credential = get_azure_sync_credential()

    producer = EventHubProducerClient(
        fully_qualified_namespace=EVENT_HUB_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        credential=credential
    )

    try:
        while True:
            price = fetch_bitcoin_price_usd()

            if price is not None:
                message = {
                    "currency": "BTC",
                    "price_usd": price,
                    "timestamp": time.time()
                }

                try:
                    batch = producer.create_batch()
                    batch.add(EventData(json.dumps(message)))
                    producer.send_batch(batch)
                    logger.info("Sent: %s", message)

                except Exception as send_error:
                    logger.error("Failed to send to Event Hub: %s", repr(send_error))
            else:
                logger.warning("Skipped sending: Invalid price")

            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Streamer stopped manually")

    finally:
        producer.close()
        logger.info("EventHub producer closed")


if __name__ == "__main__":
    stream_bitcoin_data()
