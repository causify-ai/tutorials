# PySpark API

## Overview

This document describes the core API functionality of our real-time data pipeline built using **PySpark**. The API facilitates fetching, processing, analyzing, and visualizing real-time Bitcoin market data. The implementation uses PySpark’s streaming, MLlib, and DataFrame APIs to create a fully functional end-to-end data pipeline, suitable for large-scale, distributed computing.

> 🔗 Refer to [`bitcoin_utils.py`](bitcoin_utils.py) for the complete implementation of the API.

---

## Technology Stack

* **PySpark**: For distributed data processing and machine learning (via MLlib).
* **CoinGecko API**: For real-time Bitcoin market data.
* **Spark Structured Streaming**: For micro-batch streaming data ingestion.
* **AWS S3**: For cloud storage of results (optional).
* **Matplotlib**: For data visualization.

---

## Architecture

```
                         +----------------------+
                         |  CoinGecko API       |
                         +----------+-----------+
                                    |
                              Fetch Bitcoin OHLC
                                    |
                                    v
                         +----------+-----------+
                         |  File Producer        |
                         |  (writes JSON files)  |
                         +----------+-----------+
                                    |
                                    v
                      +-------------+-------------+
                      | Spark Structured Streaming|
                      |   (read JSON -> DataFrame)|
                      +-------------+-------------+
                                    |
                +-------------------+-------------------+
                |                                   |
      +---------v--------+               +-----------v----------+
      | Aggregations     |               | MLlib GBT Regression  |
      | - Hourly Avg     |               | - Feature Engineering |
      | - Daily Stats    |               | - Train/Test Split    |
      | - Moving Avg     |               | - Evaluation          |
      +------------------+               +-----------+-----------+
                                                    |
                                                    v
                                      +-------------+--------------+
                                      | Visualization & Parquet Out|
                                      +-------------+--------------+
                                                    |
                                                    v
                                              +-----+-----+
                                              |   S3/Local|
                                              +-----------+
```

---

## API Functions and Descriptions

### 1. `fetch_price_as_ohlc()`

Fetches the latest Bitcoin price from the CoinGecko API and returns a JSON dictionary with OHLC (Open, High, Low, Close) format.

---

### 2. `start_file_producer()`

Spawns a background thread that periodically fetches new OHLC data and writes it into timestamped JSON files and a historical log file.

---

### 3. `run_streaming_query_and_writer()`

Starts a Spark Structured Streaming job that continuously ingests and processes JSON files written by the producer. It prints new batches to the console.

---

### 4. `aggregate_hourly_daily_moving_average()`

Processes historical data to compute:

* Hourly average/min/max
* Daily average/min/max
* 1-hour moving average with 30-minute slide

All results are printed using Spark DataFrame `.show()` method.

---

### 5. `train_and_evaluate_gbt_regressor()`

Trains a Gradient Boosted Tree (GBT) regression model using the following features:

* `timestamp` (numeric)
* `hour` of day
* `dayofweek`

It evaluates the model with R² and RMSE metrics and saves the predictions as a zipped Parquet file locally and uploads to AWS S3 (if environment variables are configured).

---

### 6. `plot_actual_vs_predicted_prices()`

Generates a line plot comparing actual vs predicted Bitcoin close prices over time and saves the figure as `output_plot.png`.

---

## Environment Configuration

To enable cloud uploads, add an `.env` file with the following:

```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-2
S3_BUCKET_NAME=your_bucket_name
```

These are read at runtime via `os.getenv`.

---

## How to Use the API

Import and call:

```python
from bitcoin_utils import (
    fetch_price_as_ohlc,
    start_file_producer,
    run_streaming_query_and_writer,
    aggregate_hourly_daily_moving_average,
    train_and_evaluate_gbt_regressor,
    plot_actual_vs_predicted_prices
)

start_file_producer()
run_streaming_query_and_writer()
aggregate_hourly_daily_moving_average()
train_and_evaluate_gbt_regressor()
plot_actual_vs_predicted_prices()
```

---

## References

* [PySpark Official Docs](https://spark.apache.org/docs/latest/api/python/)
* [CoinGecko API](https://www.coingecko.com/en/api)
* [Matplotlib](https://matplotlib.org/)
* [AWS S3 boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
