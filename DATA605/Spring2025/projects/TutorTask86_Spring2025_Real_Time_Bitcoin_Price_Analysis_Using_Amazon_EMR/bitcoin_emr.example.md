# Real-Time Bitcoin Price Analysis Example

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Workflow](#workflow)
- [Technologies Used](#technologies-used)
- [Sample Output](#sample-output)
- [Conclusion](#conclusion)

---

## Overview

This example demonstrates a real-time Bitcoin price analysis system that continuously fetches Bitcoin price data from a public API, stores it in Amazon S3, and processes the data using Apache Spark on Amazon EMR.

---

## Architecture

[CoinGecko API] → [bitcoin_producer.py] → [Amazon S3 (data_v2/)] → [EMR Spark Job via bitcoin_streaming_consumer_emr_debug.py] → [Amazon S3 (output_streaming/)]

---

## Workflow

1. `bitcoin_producer.py`:
   - Periodically (every 60 seconds) fetches the current Bitcoin price in USD.
   - Stores each record with a timestamp as a JSON object in an S3 bucket under `data_v2/`.

2. `bitcoin_streaming_consumer_emr_debug.py`:
   - Runs a Spark Structured Streaming job on EMR.
   - Reads new JSON files from `data_v2/`, processes them using Spark SQL functions (e.g., from_json, window), and performs a 1-minute windowed aggregation to compute the average price.
   - Writes the aggregated results to `output/` in S3 in JSON format.


---

## Technologies Used

- CoinGecko API (public cryptocurrency price API)
- Python (for scripting)
- Boto3 (to connect to Amazon S3)
- Amazon S3 (for raw and processed data)
- Apache Spark (for windowed streaming aggregation)
- Amazon EMR (to execute Spark jobs at scale)

---

## Sample Output

Sample of a raw record in `data_v2/`:
```json
{
  "timestamp": "2025-05-15T19:25:00",
  "price_usd": 71500.45
}

## Sample of a processed windowed output in output_streaming/:

{
  "window": {
    "start": "2025-05-15T19:25:00",
    "end": "2025-05-15T19:26:00"
  },
  "avg_price": 71480.22
}

