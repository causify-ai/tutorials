import faust
import requests
from datetime import datetime

app = faust.App('bitcoin-price-app', broker='kafka://localhost:9092')

class Price(faust.Record, serializer='json'):
    timestamp: str
    price_usd: float

price_topic = app.topic('btc_prices', value_type=Price)

@app.agent(price_topic)
async def process_price(prices):
    async for price in prices:
        print(f"Received BTC price at {price.timestamp}: ${price.price_usd:.2f}")

@app.timer(interval=10.0)
async def fetch_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url).json()
        current_price = response['bitcoin']['usd']
        timestamp = datetime.utcnow().isoformat()
        await price_topic.send(value=Price(timestamp=timestamp, price_usd=current_price))
    except Exception as e:
        print(f"Failed to fetch price: {e}")
