from kafka import KafkaProducer
import json
import time
import requests
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # docker-compose Kafka service
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_bitcoin_data():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin'
    params = {
        'localization': 'false',
        'tickers': 'false',
        'community_data': 'false',
        'developer_data': 'false'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()['market_data']
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'price': data['current_price']['usd'],
                'volume_24h': data['total_volume']['usd'],
                'price_change_24h': data['price_change_percentage_24h']
            }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

while True:
    data = fetch_bitcoin_data()
    if data:
        producer.send('btc_prices', data)
        print("Sent data to Kafka:", data)
    time.sleep(60)
