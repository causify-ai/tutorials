<!-- toc -->

- [Introduction](#introduction)
  * [Key Components](#key-components)
    + [1. BitcoinAPI](#1-bitcoinapi)
      - [Key Features:](#key-features)
      - [Example:](#example)
    + [2. Kafka Producer](#2-kafka-producer)
      - [Key Features:](#key-features-1)
      - [Example:](#example-1)
    + [3. Spark Consumer](#3-spark-consumer)
      - [Key Features:](#key-features-2)
      - [Example:](#example-2)
    + [4. utils.py](#4-utilspy)
      - [Key Features:](#key-features-3)
      - [Example:](#example-3)
    + [5. entrypoint.sh](#5-entrypointsh)
      - [Key Features:](#key-features-4)
      - [Example Flow:](#example-flow)
  * [Complete Workflow](#complete-workflow)
  * [Example Output](#example-output)

<!-- tocstop -->

# Introduction

This project demonstrates a full real-time data pipeline that:
- Fetches real-time Bitcoin price data using the CoinGecko API.
- Sends data to a Kafka topic.
- Consumes the Kafka stream using Spark Structured Streaming.
- Computes moving average and volatility metrics.
- Outputs results to Parquet files.


---

## Key Components

### 1. BitcoinAPI

A class to fetch Bitcoin price and volume data via the CoinGecko REST API.

#### Key Features:

- Lightweight API wrapper.
- Returns timestamped price and volume data.
- Logs output using Python’s `logging` module.

#### Example:

```python
api = BitcoinAPI()
print(api.fetch_bitcoin_price())
```

---

### 2. Kafka Producer

Streams real-time Bitcoin data to a Kafka topic called `bitcoin_prices`.

#### Key Features:

- Uses `confluent_kafka.Producer`.
- Serializes data using Avro (defined in `utils.py`).
- Sends data every 60 seconds.

#### Example:

```bash
python3 kafka_producer.py
```
<img src="https://github.com/user-attachments/assets/f1fb83ba-f397-4062-ba18-9fa6f3a39895" width="500"/>



---

### 3. Spark Consumer

Reads the Kafka topic and processes the stream using PySpark.

#### Key Features:

- Computes 5-minute moving averages of Bitcoin price.
- Computes 5-minute rolling standard deviation (volatility).
- Labels price trends (rising, falling, stable).
- Outputs to Parquet.

#### Example:

```bash
python3 spark_consumer.py
```

<img src="https://github.com/user-attachments/assets/5087a2b8-cd7a-4cc2-8b08-003056235416" width="500"/>



---

### 4. utils.py

Defines the Avro schema and contains a helper function for serializing data.

#### Key Features:

- Encodes dictionary to Avro bytes using `avro-python3`.
- Central schema definition for reuse across components.

#### Example:

```python
avro_bytes = serialize_to_avro({
  "timestamp": 1747459847,
  "price": 103559.0,
  "currency": "USD",
  "volume": 25412480008.35425
})
```


<img src="https://github.com/user-attachments/assets/5f200690-433d-4c7e-9671-16e727b8a2d0" width="500"/>

---

### 5. entrypoint.sh

Orchestrates the end-to-end pipeline execution.

#### Key Features:

- Ensures Kafka is ready before producing data.
- Starts the Kafka producer and Spark consumer.
- Lists generated output files.
- Keeps the container running.

#### Example Flow:

```bash
./entrypoint.sh
```

##### Steps:
1. Sets Java environment.
2. Waits for Kafka to be ready.
3. Cleans previous outputs.
4. Launches producer and consumer.
5. Lists output Parquet files.
6. Keeps the process alive.

![entrypoint_flow](https://github.com/user-attachments/assets/0c4ebff0-2650-4898-b7a1-48f5fc156d18)

<img src="[https://github.com/user-attachments/assets/5087a2b8-cd7a-4cc2-8b08-003056235416](https://github.com/user-attachments/assets/4199ba1d-f5c5-4b26-bc27-275476970079)" width="500"/>

---

## Complete Workflow

1. `BitcoinAPI` fetches real-time price and volume.
2. `kafka_producer.py` serializes and sends data to Kafka.
3. `spark_consumer.py` processes the stream and computes aggregates.
4. `utils.py` handles Avro serialization.
5. `entrypoint.sh` glues the components together.



<img src="https://github.com/user-attachments/assets/4199ba1d-f5c5-4b26-bc27-275476970079" width="500"/>

---


## How to Run the Pipeline

To execute the entire real-time analytics pipeline from start to finish, simply run the following command from your project root directory:

```bash
docker compose up --build

```
## This command performs the following steps:

1.Builds all Docker images and starts the required services.

2.Executes entrypoint.sh inside the main pipeline container.

3.Waits for Kafka to be ready.

4.Clears the previous output directory.

5.Starts the Kafka producer (in background).

6.Starts the Spark consumer (in blocking mode).

7.Lists the generated .parquet files once they are created.

8.Keeps the container alive to allow continuous streaming and monitoring.

---

## Example Output

### Moving Average Parquet
```
/workspace/output/bitcoin_price_avg/part-00000-abc.snappy.parquet
```

### Volatility Parquet
```
/workspace/output/bitcoin_volatility/part-00000-def.snappy.parquet
```

---
