<!-- toc -->



<!-- tocstop -->

- Author: Castelan, Emily
- Date: April 21 2025

## This project contains the following files

- `Falcon`.ipynb: a notebook describing the native API of Flacon
- `Falcon`_utils.py: code for using API of Falcon endpoint
- `Falcon`_Celery_Tasks.py and `Falcon_Celery_Tasks_lstm`.py: define Celery tasks
   additional functions are on: utils_extended.py, utils.py, functions.py
- docker_config: files set up docker environment
   include requirements.txt., docker-compose.yml, and additional files


## Project Description
This project is a real-time Bitcoin analytics platform built using [Falcon](https://falcon.readthedocs.io), a high-performance Python web framework designed for building fast APIs. The goal is to ingest, process, and analyze Bitcoin trading data at scale — supporting real-time insights and forecasting, with a strong focus on scalability and performance.

This README serves as both documentation and a development roadmap.

---

## Pipeline Overview
### 1. **Real-Time Data Ingestion**
- Connect to a WebSocket API (e.g., Binance or Coinbase Pro) to stream live Bitcoin trade data.
- Example data: `price`, `timestamp`, `volume`, `trade_id`, `order_type`

### 2. **Falcon API Endpoint (`/ingest`)**
- Incoming data is POSTed to a high-performance Falcon endpoint.
- This endpoint validates and quickly offloads the data for processing.
- Designed for low latency and high throughput.

### 3. **Distributed Processing Queue**
- Validated data is forwarded to async workers using Celery (or Redis Queue).
- Each task is handled independently in the background to avoid blocking the API.

### 4. **Analytics Tasks**
- **Anomaly Detection**: Identify sudden price changes or suspicious patterns.

### 5. **Model Training & Forecasting**
- Use historical price data to train a forecasting model:
  - LSTM (via Keras)

### 6. **Prediction API Endpoint (`/predict`)**
- Exposes a Falcon endpoint that returns the predicted price of specified window.
- Optionally supports parameters for time range, model type, or confidence interval.

### 7. **Caching and Optimization**
- Store frequent API results in RedisTS to reduce load.

### 8. **Scalability & Monitoring**
- The full system is containerized using Docker containers.
- Flower is utilized for monitoring Celery tasks.
