from confluent_kafka import Producer
import logging
import time
from template_utils import serialize_to_avro
from template_API import BitcoinAPI

_LOG = logging.getLogger(__name__)

def delivery_report(err, msg):
    """ Callback called once for each message sent to Kafka to confirm delivery """
    if err is not None:
        _LOG.error('Message delivery failed: %s', err)
    else:
        _LOG.info('Message delivered to %s [%d]', msg.topic(), msg.partition())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize Kafka producer
    producer = Producer({'bootstrap.servers': 'localhost:9092'})

    # Initialize API
    api = BitcoinAPI()

    while True:
        # Fetch Bitcoin price
        data = api.fetch_bitcoin_price()

        # Serialize to Avro
        avro_data = serialize_to_avro(data)

        # Produce to Kafka topic
        producer.produce(
            topic='bitcoin_prices',
            value=avro_data,
            callback=delivery_report
        )

        producer.flush()

        time.sleep(60)  # Wait 60 seconds before sending next price
