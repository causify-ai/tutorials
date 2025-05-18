# Bitcoin Price Forecasting System API Documentation

This document provides information about the available APIs in the Bitcoin Price Forecasting System.

## Data Collection APIs

### Get Current Bitcoin Price

```
GET /api/v1/bitcoin/price/current
```

Returns the current Bitcoin price in USD.

**Response Example:**
```json
{
  "price": 42365.78,
  "timestamp": "2025-05-16T06:45:32Z",
  "currency": "USD",
  "source": "YFinance"
}
```

### Get Historical Bitcoin Prices

```
GET /api/v1/bitcoin/price/historical
```

Returns historical Bitcoin price data.

**Query Parameters:**
- `period`: Historical data period (e.g., "1y", "6mo", "30d"). Default: "1y"
- `interval`: Data interval (e.g., "1d", "1h"). Default: "1d"
- `source`: Data source ("yfinance" or "coingecko"). Default: "yfinance"

**Response Example:**
```json
{
  "data": [
    {
      "date": "2024-05-16T00:00:00Z",
      "open": 42100.25,
      "high": 42750.18,
      "low": 41950.65,
      "close": 42365.78,
      "volume": 28765432109,
      "adjusted_close": 42365.78
    },
    ...
  ],
  "currency": "USD",
  "source": "YFinance",
  "period": "30d",
  "interval": "1d"
}
```

## Forecasting APIs

### Generate Price Forecast

```
POST /api/v1/bitcoin/forecast
```

Generates a Bitcoin price forecast using the specified model.

**Request Body:**
```json
{
  "model_type": "arima",
  "forecast_days": 14,
  "confidence_level": 95,
  "use_sentiment": true,
  "model_params": {
    "use_mcmc": false,
    "include_trend": true,
    "include_seasonality": true,
    "include_autoregressive": true
  }
}
```

**Response Example:**
```json
{
  "forecast": {
    "dates": ["2025-05-17", "2025-05-18", ...],
    "values": [43250.45, 43820.12, ...],
    "lower_bound": [42150.78, 42320.65, ...],
    "upper_bound": [44350.12, 45319.59, ...],
    "confidence_level": 95
  },
  "model_info": {
    "type": "arima",
    "params": {
      "p": 2,
      "d": 1,
      "q": 2
    },
    "metrics": {
      "mse": 1245.78,
      "rmse": 35.29,
      "mae": 28.65,
      "mape": 0.068
    }
  }
}
```

### Get Technical Indicators

```
GET /api/v1/bitcoin/indicators
```

Returns technical indicators for Bitcoin price data.

**Query Parameters:**
- `period`: Historical data period (e.g., "1y", "6mo", "30d"). Default: "30d"
- `indicators`: Comma-separated list of indicators to include (e.g., "rsi,macd,bb"). Default: "all"

**Response Example:**
```json
{
  "data": [
    {
      "date": "2025-05-16",
      "price": 42365.78,
      "rsi": 58.42,
      "macd": 125.45,
      "macd_signal": 98.25,
      "macd_hist": 27.2,
      "bb_upper": 43250.65,
      "bb_middle": 42100.78,
      "bb_lower": 40950.91
    },
    ...
  ],
  "period": "30d"
}
```

## Sentiment Analysis APIs

### Get Current Sentiment

```
GET /api/v1/bitcoin/sentiment/current
```

Returns the current Bitcoin sentiment analysis.

**Response Example:**
```json
{
  "date": "2025-05-16",
  "avg_polarity": 0.28,
  "avg_subjectivity": 0.45,
  "article_count": 24,
  "sentiment_distribution": {
    "positive": 14,
    "neutral": 8,
    "negative": 2
  },
  "top_articles": [
    {
      "title": "Bitcoin Reaches New Monthly High Amid Institutional Adoption",
      "source": "CoinDesk",
      "url": "https://www.coindesk.com/article/123",
      "published_at": "2025-05-16T04:25:18Z",
      "polarity": 0.65,
      "subjectivity": 0.48
    },
    ...
  ]
}
```

### Get Historical Sentiment

```
GET /api/v1/bitcoin/sentiment/historical
```

Returns historical Bitcoin sentiment data.

**Query Parameters:**
- `period`: Historical data period (e.g., "30d", "7d"). Default: "7d"
- `frequency`: Data frequency ("hourly" or "daily"). Default: "daily"

**Response Example:**
```json
{
  "data": [
    {
      "date": "2025-05-16",
      "avg_polarity": 0.28,
      "avg_subjectivity": 0.45,
      "article_count": 24,
      "positive_count": 14,
      "neutral_count": 8,
      "negative_count": 2
    },
    ...
  ],
  "period": "7d",
  "frequency": "daily"
}
```

### Run Sentiment Analysis

```
POST /api/v1/bitcoin/sentiment/analyze
```

Runs sentiment analysis for Bitcoin news.

**Request Body:**
```json
{
  "days_back": 7,
  "max_articles": 100
}
```

**Response Example:**
```json
{
  "status": "success",
  "analyzed_count": 87,
  "summary": {
    "avg_polarity": 0.28,
    "avg_subjectivity": 0.45,
    "positive_count": 42,
    "neutral_count": 32,
    "negative_count": 13
  },
  "execution_time_ms": 4582
}
```

## Authentication

All API endpoints require authentication using an API key.

**Authentication Header:**
```
Authorization: Bearer YOUR_API_KEY
```

API keys can be obtained by registering on the Bitcoin Price Forecasting System website.

## Rate Limiting

API requests are limited to:
- 100 requests per hour for free tier users
- 1,000 requests per hour for premium tier users

## Error Responses

All API errors follow this format:

```json
{
  "error": {
    "code": "invalid_parameters",
    "message": "The provided parameters are invalid",
    "details": ["Parameter 'model_type' must be one of: arima, lstm, transformer, ensemble"]
  }
}
```

Common error codes:
- `authentication_failed`: Invalid or missing API key
- `rate_limit_exceeded`: Too many requests
- `invalid_parameters`: Invalid request parameters
- `service_unavailable`: Service temporarily unavailable
- `internal_error`: Internal server error

## WebSocket API

The system also provides real-time updates via WebSocket connection.

### Bitcoin Price Updates

```
ws://api.bitcoinforecasting.com/ws/bitcoin/price
```

Sends real-time price updates every minute.

**Message Example:**
```json
{
  "type": "price_update",
  "data": {
    "price": 42386.45,
    "timestamp": "2025-05-16T06:48:00Z",
    "change_percent": 0.05,
    "change_amount": 20.67
  }
}
```

### Sentiment Updates

```
ws://api.bitcoinforecasting.com/ws/bitcoin/sentiment
```

Sends sentiment updates when new analysis is available.

**Message Example:**
```json
{
  "type": "sentiment_update",
  "data": {
    "timestamp": "2025-05-16T06:45:00Z",
    "avg_polarity": 0.32,
    "avg_subjectivity": 0.48,
    "trend": "increasing",
    "article_count": 5
  }
}
```