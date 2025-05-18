# ⚙️ `stream_app.py` – Faust Stream Processor for BTC Data

This script defines a **Faust streaming application** that consumes Bitcoin data from a Kafka topic and processes it in real-time.

## ✅ What It Does:
- Subscribes to the Kafka topic `btc_prices`
- Uses a `BitcoinData` record class to define message structure
- Prints formatted information about each received BTC snapshot:
  - Timestamp
  - Current price
  - 24-hour volume
  - 24-hour price change %

## 🧠 How It Works:
- Initializes a Faust app with name `btc-analysis-app`
- Uses Kafka broker at `kafka://localhost:9092`
- Defines an agent `process_btc_data` to handle the stream

## 📦 Example Console Output:
```
[2025-05-17T18:08:29Z] $103,225.00 | Vol: $18,967,440,164.00 | Change: -0.19%
```

## ⚙️ Dependencies:
- faust-streaming
