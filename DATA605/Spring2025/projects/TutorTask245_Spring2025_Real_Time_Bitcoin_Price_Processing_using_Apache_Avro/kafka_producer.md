<!-- toc -->

- [Introduction](#introduction)
  * [Key Components](#key-components)
    + [1. BitcoinAPI](#1-bitcoinapi)
    + [2. Kafka Producer](#2-kafka-producer)
  * [Complete Workflow](#complete-workflow)
  * [Example Usage](#example-usage)

<!-- tocstop -->

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
