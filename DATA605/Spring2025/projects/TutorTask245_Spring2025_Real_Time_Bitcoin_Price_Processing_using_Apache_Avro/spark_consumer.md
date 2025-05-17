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

![Spark Consumer Flow](./A_Markdown_tutorial_image_showcases_a_PySpark_stre.png)

---


