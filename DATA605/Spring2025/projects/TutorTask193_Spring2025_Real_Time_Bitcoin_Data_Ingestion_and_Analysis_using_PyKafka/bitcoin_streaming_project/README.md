# Real-Time Bitcoin Data Ingestion and Analysis using PyKafka

## Overview
This project uses Apache Kafka and PyKafka to stream live Bitcoin prices and perform basic analysis and visualization.

## Setup
1. Start Kafka and Zookeeper:
```bash
cd docker
docker-compose up
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the producer:
```bash
python run.py
```

4. Run the consumer or visualization:
```bash
python kafka/consumer.py

```