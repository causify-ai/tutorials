# Real-Time Bitcoin Price Analysis Using Amazon EMR

This project demonstrates a real-time data processing pipeline that collects Bitcoin price data from a public API, stores it in Amazon S3, and processes it using Apache Spark on Amazon EMR for time-series analysis.

---

## 🚀 Technologies Used

- **CoinGecko API** – For fetching live Bitcoin price in USD
- **Python** – Core scripting language
- **Boto3** – AWS SDK to interact with Amazon S3
- **Amazon S3** – For storing raw and processed data
- **Apache Spark (Structured Streaming)** – For windowed aggregation
- **Amazon EMR** – Cluster to run Spark jobs at scale

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| `bitcoin_producer.py` | Fetches real-time Bitcoin prices and writes JSON records to S3 (`data_v2/`) |
| `bitcoin_streaming_consumer_emr_debug.py` | Spark job that reads S3 input, performs 1-min windowed average, and writes to S3 (`output_streaming/`) |
| `bitcoin_emr_utils.py` | Reusable helper functions for API calls, S3 writes, and Spark logic |
| `bitcoin_emr.API.ipynb` | Demonstrates the API utility layer |
| `bitcoin_emr.example.ipynb` | Demonstrates full real-time example |
| `bitcoin_emr.API.md` | Markdown documenting the native and custom API layer |
| `bitcoin_emr.example.md` | Markdown explaining full system architecture and end-to-end flow |

---

## 🧪 Output

- **Raw Input:** S3 path: `s3://<your-bucket>/data_v2/`  
  JSON format:
  ```json
  {
    "timestamp": "2025-05-15T19:25:00",
    "price_usd": 71500.45
  }

## Processed Output: 
S3 path: s3://<bitcoin-price-streaming-data >/output/

Windowed JSON format:

{
  "window": {
    "start": "2025-05-15T19:25:00",
    "end": "2025-05-15T19:26:00"
  },
  "avg_price": 71480.22
}

## Status
Real-time pipeline tested and running successfully on Amazon EMR

Output verified in S3

All components structured as per project template and tutorial guidelines

## Author
Rithika Baskaran — Spring 2025


