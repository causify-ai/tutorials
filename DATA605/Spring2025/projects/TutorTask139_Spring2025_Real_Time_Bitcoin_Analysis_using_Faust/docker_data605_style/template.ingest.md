# 🔄 Faust Ingestion Agent – Bitcoin Price Producer

This module defines a Faust agent that fetches real-time Bitcoin prices from the CoinGecko API and **publishes** them to a Kafka topic for downstream processing.

---

## 🧩 Purpose

To act as the **data producer** in the streaming pipeline, sending clean and timestamped Bitcoin price data to the Kafka topic: `btc_price_topic`.

---

## 🛠️ Components

### ⚙️ Faust App Initialization

```python
app = faust.App(
    'btc-price-ingestor',
    broker='kafka://localhost:9092',
    value_serializer='json'
)
