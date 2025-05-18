# Spring2025_s3fs.API.md

## 🎯 Purpose

This markdown documents the native use of the `s3fs` API and `fetch_bitcoin_data` utility function. The purpose is to demonstrate **secure, programmatic access to cloud data (S3)** and **live API data fetching** for reproducible time series analysis.

---

## ⚙️ Native API Components

### 1. `fetch_bitcoin_data(days=365)`
- Fetches live Bitcoin market data from the **CoinGecko API**.
- Returns a Pandas DataFrame with columns:
  - `Timestamp`
  - `Price`

#### ✅ Under the Hood:
- Uses `requests.get()` to call `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart`
- Parses the JSON into a list of `[timestamp, price]` pairs
- Converts the timestamp to `datetime`
- Returns the data as a `DataFrame` in-memory (not saved to disk)

#### 📌 Why and When to Use:
- **When** you want fresh market data every time the analysis runs
- **Why**: Keeps your project reproducible without relying on static `.csv` files

---

### 2. Native `s3fs` Integration

#### ✅ What It Does:
- Initializes a secure S3 connection via `s3fs.S3FileSystem(anon=False)`
- Can **list**, **read**, and **write** to any path within the S3 bucket

#### Common Patterns Used:

* **List files in bucket:**
  ```python
  fs = s3fs.S3FileSystem(anon=False)
  fs.ls('bitcoin-timeseries-data-kv')
````

* **Read CSV file into pandas (Method 1 - Native `fs.open`):**

  ```python
  with fs.open('bitcoin-timeseries-data-kv/bitcoin_prices.csv', 'rb') as f:
      df = pd.read_csv(f)
  ```

* **Write file to S3:**

  ```python
  with fs.open('bitcoin-timeseries-data-kv/test_upload.txt', 'wb') as f:
      f.write(b'Hello from s3fs!')
  ```

* **Read CSV file into pandas (Method 2 - Direct `s3://` path):**

  ```python
  df = pd.read_csv(
      's3://bitcoin-timeseries-data-kv/bitcoin_prices.csv',
      storage_options={"anon": False}
  )
  ```

#### 📌 Why and When to Use:

* **Why**: Avoids local file dependency and centralizes data in S3
* **When**: You want shared, remote access to versioned data
* Simplifies access compared to using `boto3` (no need for manual client setup, credentials handling, or response parsing)
* Makes collaboration and deployment easier on cloud platforms (AWS, SageMaker, EMR, Airflow)

---

## ✅ Output Example from `fetch_bitcoin_data()`

```
   Timestamp         Price
0 2024-05-11  60888.216750
1 2024-05-12  60776.972079
2 2024-05-13  61507.054004
3 2024-05-14  62878.783301
4 2024-05-15  61569.113006
```

---

## 💡 Summary

The combination of:

* `fetch_bitcoin_data()` (live API)
* `s3fs` (native cloud access)

...enables a **stateless, reproducible, and cloud-native data pipeline** for time series modeling.

Compared to `boto3`, `s3fs` provides a **simpler, file-like interface** that's easier to integrate into pandas workflows — no manual JSON parsing or client management required.

This removes the need for static datasets or hardcoded local files, aligning with modern data engineering best practices.

