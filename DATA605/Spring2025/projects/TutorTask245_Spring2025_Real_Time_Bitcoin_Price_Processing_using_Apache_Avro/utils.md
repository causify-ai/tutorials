<!-- toc -->

- [Introduction](#introduction)
  * [Key Components](#key-components)
    + [1. Avro Schema Definition](#1-avro-schema-definition)
    + [2. serialize_to_avro()](#2-serialize_to_avro)
      - [Key Features:](#key-features)
      - [Example:](#example)
  * [Complete Workflow](#complete-workflow)
  * [Example Usage](#example-usage)

<!-- tocstop -->

# Introduction

This module provides helper utilities for Avro-based serialization of Bitcoin price data. It defines a reusable Avro schema and a function that serializes a Python dictionary to Avro binary format for efficient transmission over Kafka. These utilities are core to the data ingestion pipeline, ensuring all messages comply with a defined structure.

## Key Components

### 1. Avro Schema Definition

A static Avro schema is defined to structure all Bitcoin price records. This schema acts as a contract for the producer and consumer systems exchanging data.

#### Schema Fields:

- **timestamp** (`long`) – Unix time of price fetch.
- **price** (`double`) – Current Bitcoin price.
- **currency** (`string`) – Quoted currency, e.g., USD.
- **volume** (`double`) – 24-hour trade volume in USD.

The schema is parsed using `avro.schema.parse()` and held as a global variable for repeated reuse.

---

### 2. `serialize_to_avro()`

The `serialize_to_avro()` function converts a Python dictionary conforming to the schema into Avro-encoded binary format.

#### Key Features:

- **Compact and Fast**: Uses binary encoding via `BinaryEncoder` and `DatumWriter`.
- **Schema Enforced**: Ensures input dictionaries match the declared schema.
- **Kafka-Ready Output**: Suitable for use with Kafka’s byte-oriented messaging format.
- **Safe and Reusable**: Designed to be invoked repeatedly in a streaming context.

#### Example:

```python
data = {
    "timestamp": 1747460147,
    "price": 103550.0,
    "currency": "USD",
    "volume": 25325166301.682724
}

avro_message = serialize_to_avro(data)



# Complete Workflow

Bitcoin data is fetched using the API module.

The dictionary is passed to serialize_to_avro().

The function uses DatumWriter and BinaryEncoder to encode it into binary format using the declared Avro schema.

The binary is published to Kafka for downstream processing (e.g., Spark consumer).

from utils import serialize_to_avro

# Dictionary representing Bitcoin price data
btc_record = {
    "timestamp": 1747460147,
    "price": 103550.0,
    "currency": "USD",
    "volume": 25325166301.682724
}

serialized_data = serialize_to_avro(btc_record)
producer.produce(topic='bitcoin_prices', value=serialized_data)

```