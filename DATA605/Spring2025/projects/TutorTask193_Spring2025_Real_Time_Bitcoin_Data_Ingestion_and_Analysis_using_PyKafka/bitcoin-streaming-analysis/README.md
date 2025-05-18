# Real-Time Bitcoin Data Ingestion and Analysis using PyKafka

This project demonstrates a real-time streaming pipeline that ingests simulated Bitcoin price data, transmits it through Apache Kafka, and performs basic analysis and visualization using Python. It's built using `PyKafka`, `multiprocessing`, and Jupyter for live visualization.

---

## 🧱 Project Structure

```
bitcoin-streaming-analysis/
├── project/
│   ├── producer/
│   │   └── btc_producer.py
│   ├── consumer/
│   │   └── btc_consumer.py
│   ├── run_pipeline.py
│   └── btc_data.jsonl        # (auto-generated)
├── btc_analysis.ipynb        # Visualization & analysis notebook
├── requirements.txt
└── README.md
```

---

## 🔧 Setup Instructions

### 1. Prerequisites

- Python 3.8+
- [Apache Kafka](https://kafka.apache.org/downloads) (tested with `kafka_2.13-3.6.1`)
- Java 8+ (Ensure `JAVA_HOME` is set)
- [Anaconda (optional)](https://www.anaconda.com/)
- Jupyter Notebook / JupyterLab

---

### 2. Kafka Setup (Local)

Start Zookeeper:
```bash
cd C:\kafka\kafka_2.13-3.6.1
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```

Start Kafka Broker:
```bash
bin\windows\kafka-server-start.bat config\server.properties
```

Create topic:
```bash
bin\windows\kafka-topics.bat --create --topic btc-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

---

### 3. Environment Setup (Python)

Create and activate virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Or manually install:

```bash
pip install pykafka matplotlib pandas
```

---

### 4. Run the Pipeline

To start the producer and consumer:
```bash
python project/run_pipeline.py
```

Messages will be streamed into Kafka and printed live.

---

## 📊 Visualization

Open Jupyter Notebook:
```bash
jupyter notebook
```

Then open `btc_analysis.ipynb` to:
- Plot BTC price trends in real-time
- View statistical summaries (min, max, average)

---

## 📁 Output Data

All consumed BTC prices are saved in:
```
btc_data.jsonl
```

You can use this file for historical analysis.

---

## 🛑 Stopping Kafka

To stop Zookeeper and Kafka servers:
- Press `Ctrl + C` in the command window running them
- Or close the terminal sessions

---

## 🧠 Future Enhancements

- Stream real BTC data from an API (like CoinGecko)
- Add anomaly detection or moving averages
- Store data in a time-series database

---

## 📌 Author

Aman Kumar Sahu  
Spring 2025 - DATA605 Big Data Systems  
University of Maryland
