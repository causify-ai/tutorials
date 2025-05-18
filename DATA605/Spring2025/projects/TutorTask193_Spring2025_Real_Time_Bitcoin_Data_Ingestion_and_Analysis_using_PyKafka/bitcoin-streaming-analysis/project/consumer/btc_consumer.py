import json
from pykafka import KafkaClient
from config import settings

def run_consumer():
    client = KafkaClient(hosts=settings.KAFKA_BROKER)
    topic = client.topics[settings.KAFKA_TOPIC.encode()]
    consumer = topic.get_simple_consumer()

    for message in consumer:
        if message is not None:
            data = json.loads(message.value.decode())
            print(f"Consumed: {data}")
            # Future: send to analysis pipeline
