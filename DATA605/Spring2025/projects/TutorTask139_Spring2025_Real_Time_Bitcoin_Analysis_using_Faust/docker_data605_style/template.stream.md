# 🔁 Faust Stream Setup – Real-Time Bitcoin Stream Processing

This module sets up the Faust app and streaming pipeline that will ingest real-time Bitcoin price data from a Kafka topic and prepare it for further analysis.

---

## 🛠️ Components

### ⚙️ `faust.App(...)`
Initializes the Faust application:
```python
app = faust.App(
    'btc-price-stream',
    broker='kafka://localhost:9092',
    value_serializer='json'
)
