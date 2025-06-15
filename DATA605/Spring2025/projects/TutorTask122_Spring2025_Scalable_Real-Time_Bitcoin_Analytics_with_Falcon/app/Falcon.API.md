# API Documentation: Native API and Custom Software Layer

## Native API: Coinbase Exchange API

This system uses the Coinbase Exchange REST API to retrieve historical candlestick (OHLCV) data for Bitcoin. The data is used for ingestion, training, and evaluation.


### Required Parameters

- `symbol`: The trading pair (e.g., `BTC-USD`)
- `start`: Start date-time in ISO 8601 format (e.g., `2020-03-01T00:00:00Z`)
- `end`: End date-time in ISO 8601 format
- `granularity`: Time resolution in seconds  
  - `60` = 1 minute  
  - `300` = 5 minutes  
  - `900` = 15 minutes  
  - `3600` = 1 hour  
  - `86400` = 1 day

### Response Format

Each response contains a list of arrays:

---

## Custom Software Layer: Falcon + Celery + Redis

A Falcon-based REST API with background Celery workers was built on top of the Coinbase API. This software layer handles ingestion, transformation, model training, prediction, and storage.

### 1. Ingestion Endpoint

- **Route:** `/ingest/kline/{platform}`
- **Input:** JSON payload with `symbol`, `start`, `end`, `resolution`
- **Function:** Fetches historical candles and stores them in RedisTimeSeries under keys like:  ts:coinbase:{symbol}:{resolution}:{price_field}


### 2. Training Endpoint

- **Route:** `/lstm/train`
- **Input:** JSON with `model_name`, `symbol`, `resolution`, `seq_len`, `model_id`
- **Function:** Triggers the `train_lstm_from_redis` Celery task  
- Pulls normalized closing price series from Redis  
- Constructs sliding windows for training  
- Trains and saves an LSTM model (`.h5`) and normalization metadata (`.json`)

### 3. Prediction Endpoints

#### Single-Step Forecast

- **Route:** `/lstm/predict`
- **Function:**  
- Loads the trained model and normalization params  
- Pulls the latest sequence from Redis  
- Outputs 1 predicted value

#### Multi-Step Forecast

- **Route:** `/lstm/predictnsteps`
- **Function:**  
- Same as above, but returns a sequence of `nsteps` future values  
- `nsteps` is fixed at training time (direct multi-output, not recursive)

---

## Supporting Components

- **RedisTimeSeries**: Stores all ingested and processed time series data
- **Celery Workers**: Handle long-running tasks like model training and prediction
- **Jupyter Notebook**: Sends requests to Falcon API and displays results

---
# Live Trade Ingest Resource Documentation

This resource supports real-time ingestion of trade and ticker data using both WebSocket and HTTP POST methods. It is designed to handle high-frequency streaming data from platforms like Coinbase or Binance, and routes data to Celery tasks for further processing and anomaly detection.

## Class: `IngestResource`

### WebSocket Handler: `on_websocket`

**Route:**  /ingest/{platform} [WebSocket]


**Behavior:**

- Accepts a WebSocket connection for a given trading platform.
- Receives JSON-encoded messages from the stream.
- Responds with an acknowledgment containing the platform name and UTC timestamp.
- Logs each message received.
- Handles malformed JSON and disconnections gracefully.

**Usage:**

Used for direct WebSocket-based streaming where data is pushed from the exchange to the API in real time.

---

### POST Handler: `on_post`

**Route:**  /ingest/{platform} [POST]


**Expected Input:**  
- A single JSON message or a list of messages.
- Each message must include a `type` field and content related to trades or tickers.

**Message Handling Logic:**

- `type == "subscriptions"` → Ignored
- `type == "ticker"` → Routed to `process_ticker_data` (Celery task)
- `type == "trade"` → Routed to `process_trade_data` → `detect_anomaly` (chained Celery tasks)
- `msg["trades"]` list → Each trade is routed through the same `process → detect_anomaly` pipeline
- Any unrecognized message is logged with a warning

**Response:**

- On success: returns `HTTP 202 Accepted` with `{"status": "queued"}`
- On error: returns `HTTP 500` with error details

---

## Task Routing

| Message Type     | Task Chain                                             |
|------------------|--------------------------------------------------------|
| `ticker`         | `process_ticker_data.delay(...)`                      |
| `trade`          | `process_trade_data → detect_anomaly`                 |
| `trades` (list)  | `process_trade_data → detect_anomaly` (for each item) |

---

## Notes

- All messages are routed asynchronously using Celery.
- This resource allows both batch POST ingestion and continuous streaming via WebSocket.
- Platform names are passed as dynamic URL parameters (e.g., `/ingest/coinbase`).

