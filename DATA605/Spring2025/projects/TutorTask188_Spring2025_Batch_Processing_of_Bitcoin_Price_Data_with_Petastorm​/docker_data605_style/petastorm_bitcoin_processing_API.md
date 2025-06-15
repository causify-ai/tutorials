## Batch Processing of Bitcoin Price Data with Petastorm

<!-- toc -->

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Setting Up](#setting-up)
  * [Dependencies](#dependencies)
- [Data Ingestion](#data-ingestion)
- [Batch Data Storage](#batch-data-storage)
- [Utils](#utilspy)
- [Use of Petastorm](#use-of-petastorm)
- [How to run the code](#how-the-code-runs--step-by-step-overview)
<!-- tocstop -->

## Introduction
This project focuses on building an efficient pipeline to ingest, store, and analyze historical Bitcoin price data using [Petastorm](https://petastorm.readthedocs.io/). Petastorm is an open-source library developed by Uber that bridges the gap between large-scale Parquet data storage and machine learning workflows in Python.

The core objective is to:
- 🕒 Collect Bitcoin price data at fixed intervals using a public API (e.g., CoinGecko)
- 📦 Store the collected data in **Parquet format** using a defined schema
- 🧠 Prepare the dataset for **time series forecasting** using tools like TensorFlow or PyTorch
- 📊 Visualize and evaluate trends such as moving averages and volatility

Unlike traditional pipelines that rely solely on CSV or simple in-memory operations, this implementation leverages Petastorm's **schema enforcement** and **batch processing support**, making it suitable for large-scale ML applications and model training.

By completing this project, we gain hands-on experience in:
- Defining and enforcing structured schemas using Petastorm's `Unischema`
- Writing and reading data in Petastorm-compatible Parquet format
- Integrating efficient data pipelines into machine learning workflows

## Architecture Overview

The architecture of the **Batch Processing of Bitcoin Price Data with Petastorm** project consists of the following key components and stages:

### 1. **Data Ingestion**
- A Python script fetches live Bitcoin price data from the **CoinGecko API**.
- Data is collected at fixed intervals (e.g., hourly) and saved in a temporary CSV file.
- Fields include: `timestamp`, `price`.

### 2. **Batch Data Storage (Parquet Format)**
- The structured data is written to disk in **Parquet format**.
- A Petastorm-compatible schema (`BitcoinSchema`) is defined using `Unischema`.
- This enforces consistent data types (`np.int64` for `timestamp`, `np.float32` for `price`) across all records.
- `materialize_dataset()` and `make_batch_writer()` (or `Writer`) are used to write Petastorm-compatible Parquet files.
- The output folder contains:  
  - `part-*.parquet` files  
  - `_metadata` and `_common_metadata` for schema tracking

---

## Setting Up
- Pip install all the required dependencies like:
```python
# Run this if libraires are not already installed
%pip install petastorm pyarrow pandas matplotlib torch torchvision
```
### Dependencies
- To start, ensure you have imported all the dependencies:
```python
import time
import pandas as pd
import pyarrow.parquet as pq
import os
import petastorm_bitcoin_processing_utils as utils
```
---

## Data Ingestion
The **data ingestion** component is responsible for fetching real-time Bitcoin price data from a public API and preparing it for structured storage and analysis.

### Source API
- **CoinGecko API** is used for retrieving current market price data of Bitcoin.
- Endpoint: `https://api.coingecko.com/api/v3/simple/price`
- Response includes the latest price in USD and the current timestamp (UTC).

### Ingestion Strategy
- The script collects data at **fixed intervals** (e.g., every hour).
- Each fetched entry includes:
  - `timestamp`: The UTC time of retrieval
  - `price`: The current Bitcoin price in USD

### Temporary Storage
- Data is appended to a **CSV file** (e.g., `btc_24h.csv`) for intermediate storage.
- The CSV acts as a buffer for batching and transformation before conversion to Parquet.

### Data Format Example

| timestamp           | price     |
|---------------------|-----------|
| 2024-04-30 13:00:00 | 60341.23  |
| 2024-04-30 14:00:00 | 60510.11  |
| 2024-04-30 15:00:00 | 60289.77  |

### Notes
- The ingestion can be scheduled using a simple Python `time.sleep()` loop or integrated into a cron job or Airflow DAG for automation.
- Missing or invalid responses can be logged and skipped to ensure data integrity.
- Timestamps are later converted into **Unix epoch seconds** during the structuring phase.

By separating ingestion from transformation, the pipeline remains flexible and allows for:
- Real-time stream ingestion in the future
- Easy debugging and inspection of raw data
- Testing of downstream modules with static CSV samples

---

## Batch Data Storage
Once the Bitcoin price data is ingested and stored temporarily in a CSV, it is converted into a more efficient and structured format using **Parquet**, with schema enforcement provided by **Petastorm**.

### Why Parquet?
- Columnar storage optimized for analytics and machine learning.
- Efficient in terms of disk I/O and space.
- Interoperable with tools like TensorFlow, PyTorch, Pandas, and Spark.

### Petastorm Schema Definition

To ensure the structure of the dataset, a `Unischema` is defined using Petastorm:

```python
# Define schema for Bitcoin price data
BitcoinSchema = Unischema('BitcoinSchema', [
    UnischemaField('timestamp', np.str_, (), ScalarCodec(np.str_), False),
    UnischemaField('price_usd', np.float32, (), ScalarCodec(np.float32), False),
    UnischemaField('market_cap', np.float64, (), ScalarCodec(np.float64), False),
    UnischemaField('price_change_24h', np.float32, (), ScalarCodec(np.float32), False),
])
```

## Utils.py
### Key Components in `utils.py` (Data Ingestion & Storage)

This section summarizes the utility functions used for *ingesting* and *storing* Bitcoin price data.

Function like:
 - fetch_current_price
 - save_to_csv
 - save_to_parquet_arrow

These function are used to handle the data ingestion and storign of data. 

```python
# ==============================
# API Interaction Functions
# ==============================
def fetch_current_price(base_url):
    """Fetch current Bitcoin price in USD from CoinGecko"""
    endpoint = f"{base_url}/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_change': 'true'
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    
    return {
        'timestamp': datetime.now().isoformat(),
        'price_usd': data['bitcoin']['usd'],
        'market_cap': data['bitcoin']['usd_market_cap'],
        'price_change_24h': data['bitcoin']['usd_24h_change']
    }

# ==============================
# Data Saving Functions
# ==============================
def save_to_csv(df, output_dir, filename=None):
    """Save DataFrame to CSV"""
    if filename is None:
        filename = f"bitcoin_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, header=True)
    print(f"Data saved to {filepath}")
    return filepath

def save_to_parquet_arrow(df, output_path="file:///docker_data605_style/test_bitcoin_data/parquet"):
    """
    Save a Pandas DataFrame as a Parquet file readable by Petastorm (without Spark).
    
    Args:
        df (pd.DataFrame): The dataset to save.
        output_path (str): Parquet destination (can include 'file://' prefix).
    """
    # Strip file:// if present
    current_dir = os.getcwd()
    local_path = output_path.replace("file://",current_dir) if output_path.startswith("file://") else output_path

    # Create the directory if it doesn't exist
    os.makedirs(local_path, exist_ok=True)

    # Convert and save
    table = pa.Table.from_pandas(df)
    pq.write_table(table, os.path.join(local_path, "data.parquet"))

    print(f"======== Parquet file written to \n {local_path} ==========")
```

---
## Use of Petastorm
### How Petastorm is used in Data Ingestion and Data Storage
It provides a schema-enforced, efficient, and ML-compatible interface for reading and writing datasets, especially when dealing with time-series financial data like Bitcoin prices.

- **Schema Definition**:
  Petastorm's `Unischema` is used to define a structured schema for the Bitcoin dataset. This schema ensures that data types are consistent and that all records adhere to the expected structure.

- **Batch Storage**:
  Using `materialize_dataset`, the dataset is written in a Petastorm-compatible Parquet format with accompanying metadata (`_metadata`, `_common_metadata`) that supports efficient reading later.

- **Batch Reading**:
  Petastorm's `make_batch_reader` is used to load data in batches directly from Parquet files. This allows for efficient memory usage and high-speed iteration over large datasets.

### Where Else is Petastorm Used?
- **Data Processing**: Efficient batch reading using `make_batch_reader` allows scalable data transformation and filtering.

- **Time Series Analysis**: Petastorm enables loading large windows of time-series data for feature extraction.

- **Machine Learning**: Petastorm integrates smoothly with PyTorch and TensorFlow, making it easy to train models directly on Parquet-stored datasets.

---
## How the Code Runs — Step-by-Step Overview

---

### 1. Import Required Libraries
The notebook begins by importing all necessary libraries like `pandas`, `numpy`, `requests`, `petastorm`, `matplotlib`, etc., which are essential for data fetching, processing, and visualization.

---

### 2. Fetch Live Bitcoin Data
A function like `fetch_current_price()` is called, which uses the **CoinGecko API** to retrieve:
- The current Bitcoin price in USD  
- Market capitalization  
- 24-hour price change  

This data is returned as a Python dictionary.

---

### 3. Convert and Save to CSV
The live data is collected and then saved to a **CSV file** using the `save_to_csv()` function.  
This CSV acts as a raw backup or intermediate storage format for later conversion.

---

### 4. Define a Petastorm Schema
A `Unischema` called `BitcoinSchema` is defined using Petastorm. It specifies the structure and data types for:
- `timestamp` (as a string)
- `price_usd`, `market_cap`, and `price_change_24h` (as float values)

---

### 5. Convert CSV to Parquet Format
Using the `save_to_parquet_arrow()` function, the DataFrame is saved in **Parquet format** in a way that Petastorm can later read it.  
This format is:
- Columnar (optimized for analytics)
- Efficient for disk I/O
- Includes necessary Petastorm-compatible metadata files (`_metadata`, `_common_metadata`)

