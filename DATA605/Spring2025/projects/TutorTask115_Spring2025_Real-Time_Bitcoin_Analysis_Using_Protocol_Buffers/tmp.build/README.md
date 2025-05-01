
# 🧠 Real-Time Bitcoin Analysis using Protocol Buffers

This project implements a real-time data pipeline that ingests Bitcoin market data, encodes it using Protocol Buffers, stores it efficiently, and performs historical + real-time analysis.

---

## 🎯 Project Goals

- Ingest Bitcoin data from [CoinGecko API](https://www.coingecko.com/en/api)
- Serialize and store using Protocol Buffers (`bitcoin_full.proto`)
- Build a continuous streaming system for real-time capture
- Analyze combined historical + real-time trends (hourly, daily, minute-level)
- Detect anomalies and support insight generation

---

## 📦 Project Structure

```
.
├── protos/
│   └── bitcoin_full.proto                # Protobuf schema definition
├── src/
│   ├── bitcoin_full_pb2.py              # Auto-generated from .proto
│   ├── bitcoin_utils.py                 # Utility functions for parsing
│   ├── load_historical_data.py          # Pulls 30-day hourly price data
│   ├── stream_loop.py                   # Streams real-time price data (every 30s)
│   └── data/                            # Stores Protobuf data files
│       ├── bitcoin_historical_hourly.pb
│       └── bitcoin_data_YYYY-MM-DD.pb
├── bitcoin.API.ipynb                    # API logic: fetch, serialize, verify
├── bitcoin.example.ipynb                # Merged analysis of historical + live data
├── bitcoin.API.md                       # Markdown doc for API notebook
├── bitcoin.example.md                   # Markdown doc for example notebook
└── template_utils.py                    # Optional if reused
```

---

## 🧪 How It Works

### 🧩 1. Data Ingestion
- Uses `requests` to call CoinGecko's `/coins/markets` endpoint
- Maps JSON fields into the `BitcoinFullData` Protobuf schema

### 🗃️ 2. Serialization
- Messages are encoded using `.SerializeToString()`
- Saved as binary `.pb` files, with 4-byte length prefix

### 🔁 3. Real-Time Streaming
- A looping script runs every 30s and appends new data
- Data is stored daily (`bitcoin_data_YYYY-MM-DD.pb`)

### 📊 4. Analysis
- Merges 30 days of historical hourly data with live feed
- Performs:
  - Hourly trend visualization (last 24h, 3h)
  - Daily summary (min, max, mean)
  - Volatility spikes / anomaly detection
  - 15-minute rolling summary for trade insights

---

## 🚀 Getting Started

```bash
# Compile Protobuf schema
protoc --proto_path=protos --python_out=src protos/bitcoin_full.proto

# Run once to collect historical data
python3 src/load_historical_data.py

# Run real-time loop (will append every 30s)
python3 src/stream_loop.py
```

Then launch either `.ipynb` file to explore data or analysis.

---

## 👨‍💻 Author

**Mohit Saluru**  
Course: DATA605 — Spring 2025  
Project: TutorTask115 — Real-Time Bitcoin Analysis using Protocol Buffers

---

## 📚 References

- [CoinGecko Developer API](https://www.coingecko.com/en/api)
- [Protocol Buffers by Google](https://developers.google.com/protocol-buffers)
