import time
import requests
import json
from pykafka import KafkaClient
from config import settings

def fetch_btc_price():
    response = requests.get(settings.COINGECKO_API_URL)
    if response.status_code == 200:
        price = response.json()['bitcoin']['usd']
        return {'price': price, 'timestamp': time.time()}
    else:
        return None

def run_producer():
    client = KafkaClient(hosts=settings.KAFKA_BROKER)
    topic = client.topics[settings.KAFKA_TOPIC.encode()]
    producer = topic.get_sync_producer()

    while True:
        data = fetch_btc_price()
        if data:
            producer.produce(json.dumps(data).encode())
            print(f"Produced: {data}")
        time.sleep(settings.FETCH_INTERVAL)