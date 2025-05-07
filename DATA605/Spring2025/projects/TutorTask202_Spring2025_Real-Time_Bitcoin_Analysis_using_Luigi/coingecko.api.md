# 🧩 Coingecko API Integration — Native API Documentation

This documents the Coingecko API and the wrapper layer (`fetch_btc_price_history`) in `coingecko_utils.py`.

---

## 🔍 API Used

**Coingecko `/coins/bitcoin/market_chart`**
- Returns BTC-USD price history
- Used with `days=1`, `interval=minute`

---

## Wrapper Function

```python
def fetch_btc_price_history(days=1, interval="minute") -> pd.DataFrame
```

- Fetches data using `requests`
- Returns a clean Pandas DataFrame with `timestamp` and `price`

---

## Used By

| Luigi Task        | Purpose                      |
|-------------------|------------------------------|
| FetchDataTask     | Calls the API wrapper        |
| CleanDataTask     | Sorts and formats data       |
| AnalyzeDataTask   | Forecasts and flags anomalies |
| VisualizeDataTask | Plots output                 |
| AlertTask         | Logs and emails alerts       |
| StoreToS3Task     | Uploads output to S3         |

---

## Best Practices Followed

- Wrapper is invoked, not pushed
- Can run standalone or in Luigi pipelines