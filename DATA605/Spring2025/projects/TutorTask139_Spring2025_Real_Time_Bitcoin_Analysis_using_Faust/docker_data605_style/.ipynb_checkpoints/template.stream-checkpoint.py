import faust
from collections import deque

# Define Faust app
app = faust.App(
    'btc-price-stream',
    broker='kafka://localhost:9092',
    value_serializer='json'
)

# Data model
class BitcoinPrice(faust.Record, serializer='json'):
    timestamp: str
    price: float

# Kafka topic
price_topic = app.topic('btc_price_topic', value_type=BitcoinPrice)

# Table for rolling window (e.g., last 5 prices)
rolling_prices = app.Table('rolling_prices', default=list)

# Agent with analytics
@app.agent(price_topic)
async def process_price(prices):
    async for price in prices:
        window = rolling_prices['btc']
        window.append(price.price)
        if len(window) > 5:
            window.pop(0)

        # Compute rolling average
        rolling_avg = sum(window) / len(window)
        price_diff = abs(price.price - rolling_avg)
        change_pct = (price_diff / rolling_avg) * 100 if rolling_avg != 0 else 0

        print(f"[{price.timestamp}] Price: ${price.price:.2f} | Avg(5): ${rolling_avg:.2f} | Δ%: {change_pct:.2f}")

        # Detect significant change (e.g., >2% deviation)
        if change_pct > 2:
            print(f"⚠️  Significant change detected: {change_pct:.2f}% deviation")
