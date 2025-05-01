# Real-Time Bitcoin Price Streaming using Luigi (Checkpoint 1)

This project demonstrates a real-time data ingestion and preprocessing pipeline for Bitcoin (BTC-USD) prices using:

- **Coinbase Pro WebSocket API** (for live price data)
- **CSV Logging** (for persistence)
- **Luigi** (for task orchestration and data cleaning)

---

## ✅ Features Implemented

### 📡 Real-Time WebSocket Streaming
- Connects to `wss://ws-feed.exchange.coinbase.com`
- Subscribes to `BTC-USD` ticker updates
- Logs prices with timestamps to `data/btc_price_log.csv`


### 🧱 Luigi Pipeline (Partial)
- **FetchDataTask**: Reads CSV and converts to JSON
- **CleanDataTask**: Parses and sorts timestamps, saves clean CSV
- **AnalyzeDataTask** (optional): Forecast + detect anomalies (included in later stages)

---

## 📂 Folder Structure
```
bitcoin_price/
├── stream_btc_prices.py         # Real-time price logger (CSV)
├── btc_pipeline_realtime.py     # Luigi pipeline (Fetch, Clean, Analyze)
├── requirements.txt             # Python dependencies
├── data/                        # Output data folder (CSV, JSON)
└── luigi.API.ipynb

```

---

## 🛠 How to Run

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run real-time stream
```bash
python stream_btc_prices.py
```

### Run Luigi pipeline
```bash
python -m luigi --module btc_pipeline_realtime AnalyzeDataTask --local-scheduler
```

---

```

Output: `data/btc_price_sample.csv`

---

## 📌 Technologies Used

- Python 3.10
- WebSockets
- Luigi
- Pandas
- Nest AsyncIO
- Jupyter Notebook

---

## Coming Next
- Z-score anomaly detection
- PyPlot visualizations
- S3 upload + Email alerts