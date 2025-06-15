## `Bitcoin_API.py` — Fetching Bitcoin Blockchain Metrics Using an API

### Purpose of This File

This Python script is designed to **fetch real-time Bitcoin blockchain data** from the Blockchain.com API. It focuses on three important metrics: transaction count, block size, and hash rate. The data is collected in JSON format, processed using pandas, and returned as a clean time series DataFrame. This script is useful for students who are learning how to integrate APIs in data science projects.

---

### What the Code Teaches
- How to call a public REST API using Python  
- How to process JSON data into a pandas DataFrame  
- How to convert timestamps to datetime objects  
- How to clean and prepare time series data  
- How to handle network or data retrieval errors gracefully  

---

### Code Explanation

#### 1. Importing Libraries

```python
import requests  
import pandas as pd
```

These libraries are necessary for:
- Making API calls to fetch data (`requests`)  
- Working with time series and tabular data (`pandas`)  

---

#### 2. API URL Dictionary

```python
BLOCKCHAIN_API_URLS = {
    "hash_rate": "...",
    "transaction_count": "...",
    "block_size": "..."
}
```

A dictionary that holds the URLs for three Bitcoin blockchain metrics. Each metric returns 30 days of data in JSON format. This setup allows you to call any of these metrics using a single function.

---

#### 3. Function to Fetch and Format Data

```python
def fetch_bitcoin_metric(metric_name):
    ...
```

This function performs several key tasks:
- It checks if the metric name is valid (must match one of the keys in the URL dictionary).
- Sends a GET request to the API endpoint.
- Parses the JSON response into a pandas DataFrame.
- Converts UNIX timestamps (`x`) to readable datetime format.
- Sets the datetime column as the index.
- Renames the data column to `'value'` for easier processing later.

---

#### 4. Error Handling Block

```python
try:
    response = requests.get(...)
    ...
except requests.exceptions.RequestException as e:
    print(...)
    return pd.DataFrame()
```

This section ensures that if the API call fails (due to timeout, bad URL, no internet, etc.), the program prints an error and returns an empty DataFrame instead of crashing.

---

#### 5. Running the Script Directly

```python
if __name__ == "__main__":
    df = fetch_bitcoin_metric("transaction_count")
    print(df.head())
```

This block allows you to **test the script by itself**. It fetches the Bitcoin transaction count and prints the first few rows of the resulting DataFrame. This is useful for debugging or quick checks.

---

### Final Thoughts

This script is a simple and effective way for students to:
- Work with real-world financial APIs  
- Understand how blockchain metrics can be turned into time series data  
- Practice writing functions that are reusable and well-structured  
- Learn basic error handling in Python when working with external data sources  
