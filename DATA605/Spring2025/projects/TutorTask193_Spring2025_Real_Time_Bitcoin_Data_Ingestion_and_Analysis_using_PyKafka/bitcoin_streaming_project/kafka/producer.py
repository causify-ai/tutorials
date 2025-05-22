from pykafka import KafkaClient
import requests
import json
import time

KAFKA_HOST = "kafka:9092"
TOPIC = 'bitcoin_price'
API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'

def get_bitcoin_price():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def produce():
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[TOPIC.encode()]
    producer = topic.get_sync_producer()
    while True:
        price = get_bitcoin_price()
        if price is not None:
            message = json.dumps({"price": price, "timestamp": time.time()})
            producer.produce(message.encode('utf-8'))
            print("Produced:", message)
        time.sleep(5)

if __name__ == '__main__':
    produce()
