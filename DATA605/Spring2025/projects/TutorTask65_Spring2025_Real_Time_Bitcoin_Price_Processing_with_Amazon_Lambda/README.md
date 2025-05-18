# 📈 Real-Time Bitcoin Price Tracker with AWS Lambda, S3, Athena, and QuickSight

This project implements a **real-time Bitcoin price ingestion and analytics system** using multiple AWS services. It includes both **REST API-based** and **WebSocket-based** ingestion pipelines, processing logic for statistical summaries, and visualization through Amazon QuickSight.

---

## 🚀 Project Objective

> Build a real-time data ingestion and processing system to analyze Bitcoin price fluctuations using serverless AWS architecture.

---

## 🏗️ System Architecture

```
+------------+        +-------------+        +-----------------+
| CoinGecko  | -----> | Lambda (Ingest) | --> | S3: btc_data/     |
+------------+        +-------------+        +-----------------+
       ▲
       | (REST API)

+------------+        +---------------------+       +--------------------------+
| Binance WS | -----> | Lambda (WebSocket)        | --> | S3: websocket_btc_data/   |
+------------+        +---------------------+       +--------------------------+

         (Both)                 ▼
                         +---------------+
                         | Lambda (Process) |
                         +---------------+
                                |
                                ▼
                     +----------------------+
                     | S3: processed/, websocket_processed/ |
                     +----------------------+
                                |
                                ▼
                        +----------------+
                        |  Athena + QS   |
                        +----------------+
```

---

## 🔍 Features

- ✅ **Real-Time Ingestion via REST API**
  - Fetches BTC price every minute from the CoinGecko public API.
  - Scheduled using Amazon EventBridge.
  - Data stored in `btc_data/` on S3.

- ✅ **WebSocket-Based High-Frequency Ingestion**
  - Uses Binance WebSocket to capture BTC/USD updates every few seconds.
  - Deployed via a second Lambda function.
  - Data stored in `websocket_btc_data/`.

- ✅ **Processing Lambda (Summary Generator)**
  - Reads latest JSON records from S3.
  - Computes average price, timestamp range, and count.
  - Saves summary JSON to:
    - `processed/` for REST API data
    - `websocket_processed/` for WebSocket data

- ✅ **Amazon Athena + QuickSight Dashboards**
  - Athena used to query JSON data in S3.
  - QuickSight connected via manifest file or direct path.
  - Interactive visual dashboard (line chart, filters, etc.).

---

## 🧪 How to Run the Project

### 1. 📦 Set up AWS Resources

- S3 bucket: `ruthvick-btc-bucket`
- Two Lambda functions:
  - `BTCIngestREST`
  - `WebSocketBTCIngest`
- Two processing functions:
  - `BTCPriceProcessor`
  - `WebSocketBTCProcessor`
- EventBridge rules: to trigger both ingest and processing Lambdas

### 2. 🐍 Python Code Structure

```bash
deploy/
├── ingest/
│   └── lambda_function.py
├── process/
│   └── lambda_process.py
├── websocket_btc_ingestion/
│   └── src/
│       ├── lambda_websocket.py
│       └── lambda_ws_process.py
├── utils/
│   └── lambda_utils.py
├── process_utils/
│   └── lambda_utils_process.py
```

### 3. 🧬 Dependencies

Install required packages into your Lambda build folders:

```bash
pip3 install requests -t lambda_build_temp_ingest/
pip3 install requests -t lambda_build_temp_process/
```

### 4. 📤 Deployment

Upload zips to Lambda:
- Zip all `.py` files and `requests/` directory together.
- Set handler as:
  - Ingest: `lambda_function.lambda_handler`
  - Process: `lambda_process.lambda_handler`
  - WebSocket: `lambda_websocket.lambda_handler`
  - WS Process: `lambda_ws_process.lambda_handler`

---

## 📊 Sample Output

```json
{
  "timestamp": "2025-05-17T20:45:10.485284",
  "average_price_usd": 103274.17,
  "count": 8,
  "latest_timestamp": "2025-05-17T20:44:54.101718",
  "oldest_timestamp": "2025-05-17T20:44:39.718608"
}
```

---

## 📅 Schedule & Automation

- REST and WebSocket ingestion functions are triggered every 1–2 mins.
- Processing functions run every 3–5 mins to summarize.
- QuickSight can refresh dashboard hourly (or use Athena directly).

---

## 📂 Data Folder Structure

```text
ruthvick-btc-bucket/
├── btc_data/
│   └── btc_price_YYYYMMDDTHHMMSS.json
├── websocket_btc_data/
│   └── btc_ws_price_YYYYMMDDTHHMMSS.json
├── processed/
│   └── summary_YYYYMMDDTHHMMSS.json
├── websocket_processed/
│   └── summary_ws_YYYYMMDDTHHMMSS.json
```

---

## 🧠 Advanced Ideas (Optional Enhancements)

| Idea                    | Description                                                |
|-------------------------|------------------------------------------------------------|
| 📉 Volatility Flags      | Detect high % changes and add flags to output              |
| 📬 SNS Alerts            | Email if BTC drops > 5% in last 10 mins                    |
| 🧱 Store in Parquet      | Replace JSON with columnar storage for Athena              |
| 🕵️ Trend Detection       | Use moving average to detect bull/bear market              |
| 🔁 Retry/Failure Logic   | Add dead-letter queues for fault tolerance                 |

---


