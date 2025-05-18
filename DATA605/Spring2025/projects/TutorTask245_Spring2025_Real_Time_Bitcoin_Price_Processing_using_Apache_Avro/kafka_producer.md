<!-- toc -->

- [Introduction](#introduction)
  * [Key Components](#key-components)
    + [1. BitcoinAPI](#1-bitcoinapi)
    + [2. Kafka Producer](#2-kafka-producer)
  * [Complete Workflow](#complete-workflow)
  * [Example Usage](#example-usage)

<!-- tocstop -->

## What is Apache Kafka?

[Apache Kafka](https://kafka.apache.org/) is a distributed streaming platform used to build real-time data pipelines and streaming applications. Originally developed at LinkedIn, Kafka has become the industry standard for handling high-throughput, fault-tolerant, and scalable messaging systems.

### Key Features:

- **Publish-Subscribe Messaging System**: Producers publish data to topics, and consumers subscribe to those topics to read the data in real time.
- **Scalability**: Kafka scales horizontally with partitions and brokers, making it suitable for handling millions of messages per second.
- **Durability and Fault Tolerance**: Kafka persists messages on disk and replicates them across multiple brokers to ensure data reliability.
- **Real-Time Processing**: Integrates seamlessly with stream processing tools like Apache Spark, Flink, and Kafka Streams.

### Common Use Cases:

- Log aggregation
- Real-time analytics
- Event sourcing and auditing
- Metrics and monitoring pipelines
- Ingesting clickstream or sensor data

In this project, Kafka acts as a central backbone to stream real-time Bitcoin price data from a **producer** to a **Spark-based consumer** that processes and stores metrics like moving average and volatility.


# Introduction

This module runs a Kafka producer that periodically fetches real-time Bitcoin price data from the CoinGecko API, serializes it using Avro, and sends it to a Kafka topic. It is intended to be deployed in a loop for continuous real-time ingestion.

![Kafka Producer Workflow](./figures/kafka_producer_flow.png)

## Key Components

### 1. BitcoinAPI

- **Purpose**: To interface with the CoinGecko API and retrieve real-time Bitcoin price and volume data.
- **Output**: A dictionary with keys `timestamp`, `price`, `currency`, and `volume`.

### 2. Kafka Producer

- **Purpose**: To send Bitcoin price data to the Kafka topic `bitcoin_prices`.
- **Avro Serialization**: Utilizes the helper function `serialize_to_avro()` to serialize Python dictionaries.
- **Callback Support**: Implements `delivery_report()` to log successful and failed deliveries for traceability.

## Complete Workflow

1. Fetch data from `BitcoinAPI`.
2. Serialize the data using `serialize_to_avro()`.
3. Publish it to the Kafka topic `bitcoin_prices`.
4. Wait 60 seconds before repeating the process.

## Process Flowchart

<img src="https://github.com/user-attachments/assets/8a639286-3d5f-4bc5-8c93-e570f8a48955" width="500"/>


## Example Usage

```python
api = BitcoinAPI()
data = api.fetch_bitcoin_price()
avro_data = serialize_to_avro(data)
producer.produce(topic='bitcoin_prices', value=avro_data, callback=delivery_report)

Output-

Kafka Bootstrap Server: <Producer instance>
INFO:__main__:Message delivered to bitcoin_prices [0]

```
