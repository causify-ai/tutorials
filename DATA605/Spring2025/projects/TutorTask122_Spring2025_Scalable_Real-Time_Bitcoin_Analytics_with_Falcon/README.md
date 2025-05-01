<!-- toc -->



<!-- tocstop -->

- Author: Castelan, Emily
- Date: April 21 2025

<Describe all the files in the projects>

## This project contains the following template files

- `Falcon`.API.ipynb: a notebook describing the native API of Flacon
- `Falcon`.API.md: a description of the native API of Falcon
- `Falcon`.API.py: code for using API of Falcon
- `Falcon`.example.ipynb: a notebook implementing a project using <Package>
- `Falcon`.example.md: a markdown description of the project
- `Falcon`.example.py: code for implementing the project

This project contains the following working files
- `falcon_server`.API.md: a description of the native API of Falcon
- `falcon_server`.API.py: code for using API of Falcon


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
- **Sentiment Analysis** *(optional)*: Pull recent tweets about Bitcoin and score the sentiment using an NLP model.

### 5. **Model Training & Forecasting**
- Use historical and/or streamed price data to train a forecasting model:
  - Option A: [Facebook Prophet](https://facebook.github.io/prophet/)
  - Option B: LSTM (via Keras)

### 6. **Prediction API Endpoint (`/predict`)**
- Expose a Falcon endpoint that returns the predicted price (next 24h or specified window).
- Optionally supports parameters for time range, model type, or confidence interval.

### 7. **Caching and Optimization**
- Store frequent API results (e.g., recent predictions) in Redis to reduce load.
- Apply rate limiting to protect the system under heavy use.

### 8. **Scalability & Monitoring**
- The full system is containerized using Docker.
- Use Locust to simulate high request volume and test limits.
- Monitor system metrics using `prometheus-client`.
