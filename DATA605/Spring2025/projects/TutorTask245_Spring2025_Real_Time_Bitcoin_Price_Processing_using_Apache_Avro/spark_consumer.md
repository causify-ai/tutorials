<!-- toc -->

- [Introduction](#introduction)
  * [1. BitcoinAPI - Fetching Real-Time Data](#1-bitcoinapi---fetching-real-time-data)
    + [Key Features](#key-features)
    + [Example Usage](#example-usage)
  * [2. KafkaProducer - Streaming Bitcoin Prices](#2-kafkaproducer---streaming-bitcoin-prices)
    + [Key Features](#key-features-1)
    + [Example Flow](#example-flow)
  * [3. SparkConsumer - Real-Time Aggregation](#3-sparkconsumer---real-time-aggregation)
    + [Key Features](#key-features-2)
    + [Example Outputs](#example-outputs)

<!-- tocstop -->

## What is Apache Avro?

[Apache Avro](https://avro.apache.org/) is a data serialization framework developed within the Apache Hadoop ecosystem. It provides a compact, fast, binary data format that is ideal for data exchange between systems in distributed environments.

### Key Features:

- **Schema-Based**: Every Avro message is serialized with a schema, allowing dynamic typing and cross-language communication.
- **Compact and Efficient**: Binary encoding results in small, fast-to-serialize data—great for high-throughput systems like Kafka.
- **Interoperability**: Supports code generation and data exchange across languages like Python, Java, C++, etc.
- **Dynamic Typing**: Schema evolution is built-in, enabling forward/backward compatibility between versions of data structures.
- **Embedded Schemas**: Avro serializes both the schema and the data, ensuring consistent interpretation even without prior context.

### Why We Use Avro in This Project:

- **Kafka Integration**: Avro is well-suited for streaming platforms like Kafka, where consistent schema enforcement is critical.
- **Data Integrity**: Embedding the schema ensures that consumer systems can deserialize messages even as schema evolves.
- **Serialization Utility**: Our `utils.py` script uses Avro to encode Bitcoin price data into a compact binary format before sending it to the Kafka topic `bitcoin_prices`.

### Example:

```python
from utils import serialize_to_avro

data = {
    "timestamp": 1747459847,
    "price": 103559.0,
    "currency": "USD",
    "volume": 25412480008.35425
}

avro_bytes = serialize_to_avro(data)
```
---

## What is Apache Spark?

[Apache Spark](https://spark.apache.org/) is an open-source distributed computing system designed for fast and general-purpose data processing. It provides an interface for programming entire clusters with implicit data parallelism and fault tolerance.

### Key Features:

- **Unified Analytics Engine**: Supports batch processing, streaming, machine learning (MLlib), and graph computation (GraphX).
- **In-Memory Computation**: Performs transformations and actions on data in memory, significantly boosting performance over traditional disk-based engines like Hadoop MapReduce.
- **Ease of Use**: Provides high-level APIs in Python (PySpark), Java, Scala, and R, along with powerful SQL support via Spark SQL.
- **Fault Tolerance**: Automatically recovers lost data using lineage information stored in its resilient distributed datasets (RDDs).
- **Stream Processing**: Through Spark Structured Streaming, it enables real-time data analysis using the same DataFrame/Dataset API as batch jobs.

### Common Use Cases:

- Real-time analytics dashboards
- ETL (Extract, Transform, Load) workflows
- Machine learning model training and prediction
- Processing large-scale logs and sensor data

In this project, **Apache Spark Structured Streaming** consumes real-time Bitcoin price data from Kafka, computes **moving averages**, **volatility**, and **trend labels**, and outputs the results into Parquet files for further analysis.

---

## What is Apache Parquet?

[Apache Parquet](https://parquet.apache.org/) is a columnar storage format optimized for analytics workloads. It is designed for efficient data storage and retrieval, especially in big data processing frameworks like Apache Spark, Hive, and Drill.

### Key Features:

- **Columnar Format**:
  - Stores data column-wise instead of row-wise.
  - Enables efficient scanning and compression of specific columns.

- **Efficient Storage**:
  - Reduces I/O by reading only the required columns.
  - Applies compression techniques like run-length and dictionary encoding.

- **Schema Support**:
  - Strongly typed with schema evolution capabilities.
  - Supports complex nested data types (arrays, structs, maps).

- **Interoperable**:
  - Works across languages (Java, Python, C++) and data engines (Spark, Hive, Impala, etc.).

### Why We Use Parquet in This Project:

- **Optimized Analytics**: Ideal for storing computed metrics like moving averages and volatility from Spark.
- **Fast Reads**: Spark can read only the necessary columns for downstream computations or dashboards.
- **Compact Output**: Reduces storage footprint and speeds up file transfers.

### Output Examples:

After running the pipeline, you’ll find Parquet outputs saved in the `output/` folder:

---

# Introduction

This project builds a real-time data pipeline to stream Bitcoin price data using the CoinGecko API, Kafka, and Apache Spark Structured Streaming. The pipeline performs periodic ingestion of Bitcoin prices, produces messages to Kafka in Avro format, and consumes them using PySpark for aggregation and volatility analysis. 

---

## 1. BitcoinAPI - Fetching Real-Time Data

### Key Features

- **Fetches live Bitcoin price** from CoinGecko's public API.
- Returns timestamped output with price, volume, and currency.
- Logging support via `_LOG.info()` and `_LOG.error()`.

### Example Usage

```python
api = BitcoinAPI()
result = api.fetch_bitcoin_price()
print(result)
```

Sample Output:
```json
{
  "timestamp": 1747459847,
  "price": 103559.0,
  "currency": "USD",
  "volume": 25412480008.35425
}
```

---

## 2. KafkaProducer - Streaming Bitcoin Prices

### Key Features

- Uses `confluent_kafka.Producer` to push serialized Avro messages to Kafka.
- Wraps CoinGecko API in a loop to stream data every 60 seconds.
- Includes delivery callback confirmation for message acknowledgment.

```python
producer = Producer({'bootstrap.servers': 'kafka:9092'})
data = api.fetch_bitcoin_price()
avro_data = serialize_to_avro(data)
producer.produce(topic='bitcoin_prices', value=avro_data, callback=delivery_report)
```

### Example Flow

![Kafka Producer Flow](./A_flowchart_in_the_image_presents_a_Kafka_Producer.png)

---

## 3. SparkConsumer - Real-Time Aggregation

### Key Features

- **Kafka stream reader** configured using `spark.readStream`.
- **Windowed aggregations** every 5 minutes to compute:
  - Average price
  - Price volatility (std dev)
  - Trend classification (rising/falling/stable)
- Writes output as **Parquet** files with **checkpointing** enabled.

```python
trend_df = trend_df.withColumn(
    "trend",
    when(col("avg_price") > col("prev_price") * 1.01, "rising")
    .when(col("avg_price") < col("prev_price") * 0.99, "falling")
    .otherwise("stable")
)
```

### Example Outputs

Parquet files generated:

- `/workspace/output/bitcoin_price_avg/`
- `/workspace/output/bitcoin_volatility/`

Sample Output:
```json
{
  "start": "2025-05-17T05:00:00",
  "end": "2025-05-17T05:05:00",
  "avg_price": 103570.0,
  "std_dev": 25.3,
  "sample_count": 5,
  "trend": "rising"
}
```

### Processing Flow

<img src="https://github.com/user-attachments/assets/c31632b1-a3a5-4044-9d44-14673e9216b0" alt="spark_consumer_flow" width="600"/>


![spark_consumer_flow](https://github.com/user-attachments/assets/c31632b1-a3a5-4044-9d44-14673e9216b0)

---


