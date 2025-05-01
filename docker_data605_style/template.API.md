# `template.API.py` — Real-Time Bitcoin Data Ingestion Module

This module provides an interface to fetch real-time Bitcoin blockchain metrics using the [Blockchain.com API](https://www.blockchain.com/api/charts-api).

---

## ✅ Supported Metrics

- `transaction_count`: Total number of Bitcoin transactions per day
- `hash_rate`: Estimated average hash rate (terahashes per second)
- `block_size`: Average block size in MB

---

## 🚀 Function

### `fetch_bitcoin_metric(metric_name: str) -> pd.DataFrame`

Fetches time series data from Blockchain.com.

**Parameters:**
- `metric_name` (str): One of `'transaction_count'`, `'hash_rate'`, `'block_size'`

**Returns:**
- A Pandas DataFrame with:
  - Datetime index (`x`)
  - `value` column

---

## 📦 Example Usage

```python
from template import API

df = API.fetch_bitcoin_metric("hash_rate")
print(df.head())