import faust
from datetime import datetime

class BitcoinData(faust.Record, serializer='json'):
    timestamp: str
    price: float
    volume_24h: float
    price_change_24h: float

app = faust.App(
    'btc-analysis-app',
    broker='kafka://localhost:9092',  # <- crucial
    value_serializer='json',
)

btc_topic = app.topic('btc_prices', value_type=BitcoinData)

@app.agent(btc_topic)
async def process_btc_data(stream):
    async for data in stream:
        print(f"[{data.timestamp}] ${data.price:.2f} | Vol: ${data.volume_24h:,.2f} | Change: {data.price_change_24h:.2f}%")
