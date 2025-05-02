import faust
from datetime import datetime
import requests

# Define Faust app
app = faust.App(
    'btc-price-ingestor',
    broker='kafka://localhost:9092',
    value_serializer='json'
)

# Define the model
class BitcoinPrice(faust.Record, serializer='json'):
    timestamp: str
    price: float

# Define the topic to publish to
price_topic = app.topic('btc_price_topic', value_type=BitcoinPrice)

# Function to fetch BTC price
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        price = data['bitcoin']['usd']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return BitcoinPrice(timestamp=timestamp, price=price)
    except requests.exceptions.RequestException as e:
        print(f"Fetch error: {e}")
        return None

# Faust agent to periodically send data to Kafka
@app.timer(interval=10.0)  # every 10 seconds
async def publish_price():
    price_data = fetch_bitcoin_price()
    if price_data:
        await price_topic.send(value=price_data)
        print(f"[{price_data.timestamp}] Sent BTC price: ${price_data.price}")
