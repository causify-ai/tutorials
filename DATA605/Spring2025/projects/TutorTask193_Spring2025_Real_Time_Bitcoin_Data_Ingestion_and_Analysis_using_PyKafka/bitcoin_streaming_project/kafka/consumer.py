from pykafka import KafkaClient
import json
import csv
import os

KAFKA_HOST = "kafka:9092"
TOPIC = 'bitcoin_price'

JSON_FILE = 'output/bitcoin_data.jsonl'
CSV_FILE = 'output/bitcoin_data.csv'

os.makedirs('output', exist_ok=True)

# Initialize CSV with headers if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'price'])
        writer.writeheader()

def write_to_jsonl(data):
    with open(JSON_FILE, 'a') as f:
        json.dump(data, f)
        f.write('\n')

def write_to_csv(data):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'price'])
        writer.writerow(data)

def consume():
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[TOPIC.encode()]
    consumer = topic.get_simple_consumer()
    for message in consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            print("Consumed:", data)
            write_to_jsonl(data)
            write_to_csv(data)

if __name__ == '__main__':
    consume()
