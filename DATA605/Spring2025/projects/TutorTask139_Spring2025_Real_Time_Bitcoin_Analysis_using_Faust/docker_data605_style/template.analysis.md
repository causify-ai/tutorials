# 📈 Bitcoin Time Series Forecasting with ARIMA

This module loads historical Bitcoin price data and applies an ARIMA model to forecast future values.

---

## 🧩 Purpose

To analyze historical Bitcoin prices (from Kafka stream or saved file) and:
- Fit an ARIMA time series model
- Forecast future prices
- Visualize historical and predicted trends

---

## 🗂️ Input

Assumes a local file named `btc_prices.json` containing one JSON object per line:
```json
{"timestamp": "2025-05-01 22:30:00", "price": 64200.12}
