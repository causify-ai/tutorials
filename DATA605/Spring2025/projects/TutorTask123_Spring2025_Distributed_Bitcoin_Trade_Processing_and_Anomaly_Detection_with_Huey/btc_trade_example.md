# Distributed Bitcoin Trade Processing and Anomaly Detection

---

## Introduction

This project builds a distributed, fault-tolerant system for real-time Bitcoin trade ingestion, aggregation, anomaly detection, sentiment correlation, and performance monitoring.  
The system is built using **Huey** for task orchestration, **Redis** for durability, and **Prometheus**/**Grafana** for monitoring and visualization.

Designed for high-frequency trade streams (10,000+ trades/hour), the system ensures reliability through retries and fault tolerance, while providing real-time insights via alerts and dashboards.

---

## System Architecture

| Component | Description |
|:---|:---|
| **Real-Time Ingestion** | Simulated or live Bitcoin trades streamed into Huey task queue. |
| **Aggregation** | Trades grouped into 1-minute and 5-minute OHLC (Open, High, Low, Close) buckets. |
| **Anomaly Detection** | Prices flagged if 3σ outside rolling averages, with Slack alert notifications. |
| **Sentiment Analysis** | Recent Reddit posts analyzed using VADER sentiment scores. |
| **Monitoring and Alerts** | Prometheus metrics and Slack alerts ensure system observability. |

---

## Main Pipeline Components

### 1. Trade Ingestion

- Trades are simulated or streamed via WebSocket or APIs.
- Each trade triggers the `process_trade` Huey task, which orchestrates:
  - Aggregation
  - Anomaly check
  - Sentiment correlation

---

### 2. Aggregation Task

```python
aggregate_trade(trade_data)
