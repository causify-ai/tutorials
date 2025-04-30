# Bitcoin Price Streaming API Tutorial (Checkpoint 1)

## Overview

This document provides an overview of the native API integration used in the first checkpoint of the Bitcoin Price Analytics project. The focus is on building a real-time Bitcoin price ingestion system using the Coinbase Pro WebSocket API and implementing the first two Luigi tasks: data fetching and cleaning.

---

## Stream API Implementation

**File:** `stream_btc_prices.py`

- Connects to the Coinbase WebSocket feed at `wss://ws-feed.exchange.coinbase.com`.
- Subscribes to the `ticker` channel for `BTC-USD`.
- Continuously listens for real-time price updates.
- Logs incoming messages to `data/btc_price_log.csv` with timestamp and price.

---

## Luigi Tasks Implemented

**File:** `btc_pipeline_realtime.py`

### 1. `FetchDataTask`

- Reads from the `btc_price_log.csv` created by the WebSocket streamer.
- Converts the CSV into a structured JSON format.
- Output: `data/raw_<date>.json`

### 2. `CleanDataTask`

- Loads the raw JSON data.
- Converts timestamps and sorts the data chronologically.
- Output: `data/clean_<date>.csv`

---

## Requirements

All code depends on the following libraries (see `requirements.txt`):

- `websockets`, `luigi`, `pandas`, `json`, `csv`, `datetime`, `os`

---

## Notes

- The pipeline is modular and tasks are interdependent.
- This checkpoint demonstrates core real-time ingestion and preprocessing logic.
- Later checkpoints will include analysis, visualization, and alerting.