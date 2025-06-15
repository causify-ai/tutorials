# Bitcoin EMR Utility API Tutorial

## Table of Contents
- [Introduction](#introduction)
- [Native API Used](#native-api-used)
- [Our Utility Layer](#our-utility-layer)
- [Key Functions](#key-functions)
  - [fetch_bitcoin_price()](#fetchbitcoin_price)
  - [get_current_timestamp()](#get_current_timestamp)
  - [save_price_to_s3()](#save_price_to_s3)
- [Example Usage](#example-usage)
- [Conclusion](#conclusion)

---

## Introduction

This tutorial explains the utility layer built for fetching real-time Bitcoin prices from a public API and storing the results in Amazon S3. These utility functions are used by producer scripts and Jupyter notebooks to simulate real-time data pipelines.

---

## Native API Used

- **CoinGecko API**: Used to fetch the current price of Bitcoin in USD.
- **Boto3 (AWS SDK for Python)**: Used to programmatically write JSON files to an S3 bucket.

---

## Our Utility Layer

All helper logic is implemented in `bitcoin_emr_utils.py`, which serves as the foundation for producer scripts and Spark-based processing.

---

## Key Functions

### fetch_bitcoin_price()

- Calls the CoinGecko API.
- Returns the current Bitcoin price in USD.
- Raises an exception if the response is not valid.

### get_current_timestamp()

- Returns the current timestamp in ISO 8601 format with timezone.
- Used to timestamp each Bitcoin price record.

### save_price_to_s3(bucket, folder, filename_prefix="price", price_usd=None)

- Constructs a record using the current timestamp and given price.
- Uploads the JSON object to the given S3 bucket/folder.
- Automatically fetches the price if `price_usd` is not provided.

---

## Example Usage

```python
from bitcoin_emr_utils import fetch_bitcoin_price, save_price_to_s3

price = fetch_bitcoin_price()
save_price_to_s3(bucket='bitcoin-price-streaming-data', folder='data_v2', price_usd=price)

