# 🔄 `btc_producer.py` – Real-Time Bitcoin Data Fetcher

This Python script is responsible for fetching real-time Bitcoin price data and sending it into a Kafka topic for downstream processing.

## ✅ What It Does:
- Queries the **CoinGecko API** every 60 seconds to get:
  - Current BTC price in USD
  - 24-hour trading volume
  - 24-hour price change percentage
- Formats the data into JSON
- Sends the data to Kafka topic `btc_prices` using the `KafkaProducer`

## 🧠 How It Works:
- Uses `requests` to hit the CoinGecko API
- Serializes data with `json.dumps`
- Connects to Kafka running on `localhost:9092`
- Sends one message per minute to `btc_prices` topic

## 📦 Example Output:
```
Sent data to Kafka: {
    'timestamp': '2025-05-18T00:34:10.697526',
    'price': 103246,
    'volume_24h': 18967440164,
    'price_change_24h': -0.19224
}
```

## ⚙️ Dependencies:
- kafka-python
- requests
