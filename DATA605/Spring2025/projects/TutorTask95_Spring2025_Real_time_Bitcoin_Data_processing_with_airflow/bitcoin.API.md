<!-- toc -->

- [Bitcoin API Tutorial](#bitcoin-api-tutorial)
  * [Table of Contents](#table-of-contents)
  * [General Guidelines](#general-guidelines)
  * [Overview](#overview)
  * [Key Functions](#key-functions)
    + [fetch_bitcoin_price()](#fetch_bitcoin_price)
    + [save_price_to_csv()](#save_price_to_csv)
    + [compute_moving_average()](#compute_moving_average)
    + [upload_to_s3()](#upload_to_s3)
  * [Environment Compatibility](#environment-compatibility)
  * [Logging](#logging)

<!-- tocstop -->

# Bitcoin API Tutorial

## Table of Contents

This markdown documents the available API functions for the Bitcoin Data Pipeline and how to use them in both Airflow and local environments.


## General Guidelines

- This markdown documents the native API and wrapper functions implemented in `bitcoin_utils.py`.
- It complements the example usage notebook `bitcoin.API.ipynb`.

## Overview

This tutorial introduces a simple API for real-time Bitcoin price tracking using the CoinGecko API. The functions are modular and reusable, designed for Airflow pipelines or standalone scripts. They fetch, store, process, and optionally upload Bitcoin price data.

## Key Functions

### fetch_bitcoin_price()

Fetches the latest Bitcoin price in USD from the CoinGecko public API.

- **Returns**: A dictionary with the UTC timestamp and price in USD.
- **Usage**:
  ```python
  data = fetch_bitcoin_price()
  ```
### save_price_to_csv()

Calls `fetch_bitcoin_price()` and saves the returned record to a CSV file.

- Appends to the file if it exists.
- Uses the path defined in the `BITCOIN_RAW_PATH` environment variable, or defaults to `/opt/airflow/data/bitcoin_raw.csv`.

---

### compute_moving_average(window=2)

Reads the raw CSV file, calculates a rolling moving average of the price, and saves the processed result.

- Default window size is 2.
- Output is written to the path defined in the `BITCOIN_PROCESSED_PATH` environment variable.

---

### upload_to_s3(bucket_name, key_path)

Uploads the processed CSV file to an AWS S3 bucket.

- Requires proper AWS credentials via environment variables or IAM role.
- Raises an exception and logs an error if the upload fails.

---

## Environment Compatibility

These functions are designed to work in both **Docker/Airflow** environments and **local development setups**.

- Docker uses default paths like `/opt/airflow/data/...`.
- Local runs can override these paths using:

  ```python
  os.environ["BITCOIN_RAW_PATH"] = "./data/bitcoin_raw.csv"
  os.environ["BITCOIN_PROCESSED_PATH"] = "./data/bitcoin_processed.csv"
  ```
  To apply the override during local development, reload the module after setting environment variables:

```python
import importlib
import bitcoin_utils
importlib.reload(bitcoin_utils)
```
## Logging

All API functions use the `logging` module to report activity and errors.

- `logger.info(...)` is used for successful operations such as fetching or saving data.
- `logger.error(...)` is triggered if something goes wrong, such as missing files or S3 upload failures.

Logging is especially useful when running the pipeline inside Airflow, as messages appear in the task logs for each operator.

