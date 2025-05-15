# Real-Time Bitcoin Price Analysis Using Amazon EMR

This project focuses on **real-time ingestion and processing of Bitcoin price data** using Amazon EMR and Apache Spark.  
Bitcoin prices are fetched from a public API (such as CoinGecko) every few seconds and saved to Amazon S3. These records are then processed using Spark jobs running on an EMR cluster to enable near real-time analytics.

---
 HEAD

## 📌 Objectives
- Fetch real-time Bitcoin price data from public APIs
- Process data using PySpark on Amazon EMR
- Perform time-series analysis (e.g., moving averages, price fluctuations)
- Store raw and processed data in Amazon S3

---

## 📂 Project Structure
DATA605/Spring2025/projects/TutorTask86_Spring2025_Real_Time_Bitcoin_Price_Analysis_Using_Amazon_EMR/ 
├── bitcoin_ingest.API.py
├── bitcoin_processing.example.py 
├── bitcoin_streaming.example.py 
├── bitcoin_timeseries.example.py 
├── spark_test.py 
└── template.API.ipynb


---

## 🔧 Technologies
- Amazon EMR
- Apache Spark (PySpark)
- AWS S3
- CoinGecko API / CryptoCompare API
- Python

---

## ✅ Next Steps
- Add Docker setup
- Finalize automation using EMR steps
- Complete write-up and submit final PR

---

*Author: Rithika Baskaran*  
*Date: Spring 2025*
=======

## ✅ Project Objective

- Simulate real-time Bitcoin price ingestion using a producer script
- Save price records to Amazon S3 in near real-time
- Configure and run a Spark job using EMR to process the records
- Demonstrate the real-time pipeline through API, notebook, and markdown tutorials

---

## 🔧 Technologies Used

- **Amazon EMR** — cluster-based execution of Apache Spark
- **Amazon S3** — used as a storage sink for real-time records
- **Apache Spark (PySpark)** — for data transformation and analysis
- **Python** — for scripting and logic
- **CoinGecko API** — source for Bitcoin price data

---

## 📂 Directory Structure

DATA605/Spring2025/projects/TutorTask86_Spring2025_Real_Time_Bitcoin_Price_Analysis_Using_Amazon_EMR/
├── bitcoin_streaming_consumer_emr.py
├── bitcoin_producer.py
├── bitcoin_emr_utils.py
├── bitcoin_emr.API.ipynb
├── bitcoin_emr.example.ipynb
├── bitcoin_emr.API.md
├── bitcoin_emr.example.md
└── README.md

---

## 🚀 Real-Time Data Flow

1. `bitcoin_producer.py`: Fetches real-time Bitcoin prices from CoinGecko API and saves them to S3.
2. `bitcoin_streaming_consumer_emr.py`: Processes incoming JSON files from the S3 bucket using Apache Spark.
3. Spark job is launched via Amazon EMR cluster and performs transformations or aggregations.
4. Final results are written back to S3.

---

## 🧪 Sample Output (Stored in S3)

```json
{
  "timestamp": "2025-05-15T13:40:00",
  "price_usd": 71234.56
}


 3544db0 (Updated README to reflect real-time structure and progress for PR #2)
