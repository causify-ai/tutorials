# Falcon Example Notebook: Real-Time Bitcoin Ingestion and Forecasting

This notebook demonstrates how to use the Falcon API along with Redis, Celery, and an LSTM model to process and forecast Bitcoin closing prices using historical data from the Coinbase API.

## System Overview

1. **Notebook** acts as the user interface and sends HTTP requests.
2. **Falcon API** receives these requests and routes them to:
3. **Celery Workers** that process the data, perform training or prediction, and interact with:
4. **RedisTimeSeries**, which stores the ingested data and serves it to the model.
5. The **Notebook** retrieves the final prediction results.

### Summary

This example demonstrates the end-to-end flow of:

1. Ingesting data using Falcon
2. Storing it in Redis
3. Preparing it for training and prediction with LSTM models via background tasks


## Native API Used

### Coinbase Candle Endpoint  
https://api.exchange.coinbase.com/products/{symbol}/candles


- Parameters:
  - `symbol` (e.g., "BTC-USD")
  - `start`, `end` (ISO 8601 timestamp)
  - `granularity` (e.g., 86400 for daily)
- Response format: `[ time, low, high, open, close, volume ]`

## Custom Falcon Endpoint Used

### Route: `/ingest/kline/coinbase` (POST)

The notebook uses the `select_candles()` function to post a payload to this route.

### Payload Example

```json
{
  "model_id": 3,
  "symbol": "BTC-USD",
  "resolution": "1d",
  "start": "2024-02-01T00:00:00Z",
  "end": "2024-04-01T00:00:00Z"
}
```
### Result

The Falcon API triggers a Celery task to ingest historical candles from Coinbase.
The candles are stored in RedisTimeSeries under a structured key for later use.