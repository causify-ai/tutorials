import json
from pykafka import KafkaClient
from pykafka.common import OffsetType

KAFKA_HOST = 'kafka:9092'
TOPIC = 'bitcoin_price'
GROUP = 'btc_consumer_group'

def process_message(data):
    print(f"[BalancedConsumer] Received: {data}")

def main():
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[TOPIC.encode()]

    consumer = topic.get_balanced_consumer(
        consumer_group=GROUP.encode(),
        auto_commit_enable=True,
        zookeeper_connect='localhost:2181',
        auto_offset_reset=OffsetType.LATEST
    )

    print(f"[BalancedConsumer] Started in group '{GROUP}'...")

    for message in consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            process_message(data)

if __name__ == '__main__':
    main()
