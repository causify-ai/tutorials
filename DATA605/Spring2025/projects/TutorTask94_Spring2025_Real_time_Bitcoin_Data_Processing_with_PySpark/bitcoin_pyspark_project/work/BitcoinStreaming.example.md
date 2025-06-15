<!-- toc -->

- [Real-time Bitcoin Data Processing with PySpark API](#real-time-bitcoin-data-processing-with-pyspark-api)  
  - [Table of Contents](#table-of-contents)  
    - [Hierarchy](#hierarchy)  
  - [General Guidelines](#general-guidelines)  
  - [API Reference](#api-reference)  
    - [initialize_spark_session](#initialize_spark_session)  
    - [configure_streaming_paths_and_schedule](#configure_streaming_paths_and_schedule)  
    - [fetch_price_as_ohlc](#fetch_price_as_ohlc)  
    - [start_file_producer](#start_file_producer)  
    - [stream_and_display_batches](#stream_and_display_batches)  
    - [run_streaming_query_and_writer](#run_streaming_query_and_writer)  
    - [count_historical_records](#count_historical_records)  
    - [preview_historical_data](#preview_historical_data)  
    - [aggregate_hourly_daily_moving_average](#aggregate_hourly-daily-moving-average)  
    - [prepare_features_for_linear_regression](#prepare_features_for-linear-regression)  
    - [train_and_predict_with_linear_regression](#train_and-predict-with-linear-regression)  
    - [train_and_evaluate_gbt_regressor](#train_and-evaluate-gbt-regressor)  
    - [plot_actual_vs_predicted_prices](#plot_actual-vs-predicted-prices)  

<!-- tocstop -->

# Real-time Bitcoin Data Processing with PySpark API

## Table of Contents

The markdown code above is used to generate this TOC automatically.

### Hierarchy

- `#` Level 1: Title of the tutorial (this file)  
- `##` Level 2: Major sections (Table of Contents, General Guidelines, API Reference)  
- `###` Level 3: Individual functions under API Reference  

## General Guidelines

- This document describes the native Python API exposed by the `bitcoin_utils.py` module.  
- All code examples in `bitcoinApi.ipynb` import these functions; avoid embedding complex logic directly in notebooks.  
- Refer to the main [README](README.md) for overall project setup, environment configuration, and Docker instructions.  
- Document each function with:
  - Purpose and high-level behavior  
  - Parameters (if any) and return value  
  - Any side effects (e.g., file I/O, background threads, S3 uploads)  

---

## API Reference

### initialize_spark_session

```python
spark = initialize_spark_session()


This document explains every cell in bitcoin.example.ipynb`, detailing its purpose and the functions imported from the `bitcoin_utils.py` utilities file.

---

### Cell 1: Markdown
**Original Content:**
```markdown
# Bitcoin Forecasting Pipeline Example
This notebook shows the full pipeline using `bitcoin_utils.py` to forecast Bitcoin prices.
```

**Explanation:**
This opening cell provides the title and high-level overview of the notebook. It tells the reader that the notebook demonstrates an end-to-end Bitcoin forecasting pipeline, leveraging helper functions from the `bitcoin_utils.py` module to perform tasks such as data ingestion, streaming, aggregation, modeling, and visualization.

---

### Cell 2: Code
```python
from bitcoin_utils import initialize_spark_session
spark = initialize_spark_session()
```

**Explanation:**
- Imports the `initialize_spark_session` function from the `bitcoin_utils.py` utility file.
- Calls `initialize_spark_session()`, which creates and returns a configured SparkSession named **BitcoinPipeline**.
- Stores the SparkSession object in the variable `spark`, which will be used for all subsequent Spark-related operations.

---

### Cell 3: Markdown
**Original Content:**
```markdown
## Fetches the latest Bitcoin OHLC price data from the CoinGecko API and returns it as a dictionary.
```

**Explanation:**
This cell introduces the purpose of the next code cell. It explains that the following function call will fetch the latest Open-High-Low-Close (OHLC) Bitcoin price data from the CoinGecko API and return it in dictionary form, including timestamp and volume information.

---

### Cell 4: Code
```python
from bitcoin_utils import fetch_price_as_ohlc
fetch_price_as_ohlc()
```

**Explanation:**
- Imports the `fetch_price_as_ohlc` function.
- Executes the function, which:
  1. Sends an HTTP request to the CoinGecko API endpoint.
  2. Parses the JSON response to extract OHLC values and total volume.
  3. Wraps the results in a dictionary with keys: `Datetime`, `Open`, `High`, `Low`, `Close`, and `Volume`.
- Displays the returned dictionary, demonstrating how raw price data is obtained.

---

### Cell 5: Code
```python
from bitcoin_utils import start_file_producer
start_file_producer()
```

**Explanation:**
- Imports the `start_file_producer` function.
- When invoked, this function:
  1. Runs a background loop for a fixed duration (default: 90 seconds).
  2. Every 30 seconds, calls `fetch_price_as_ohlc()` to retrieve new OHLC data.
  3. Writes each new record as a JSON file into the `Data/stream` directory.
  4. Appends each record to a growing history log in `Data/bitcoin_combined.json`.
- Outputs file write notifications to the console as it produces data.

---

### Cell 6: Markdown
**Original Content:**
```markdown
## Starts a background thread that fetches and writes Bitcoin OHLC data every 30 seconds
```

**Explanation:**
This markdown cell clarifies that the file producer from the previous step is running in a separate thread, continuously fetching and storing new Bitcoin price records at 30-second intervals without blocking further notebook execution.

---

### Cell 7: Markdown
**Original Content:**
```markdown
## Starts the Spark Structured Streaming job to process new Bitcoin data batches while the producer runs in parallel.
```

**Explanation:**
This cell describes the next action: launching a Spark Structured Streaming job that will monitor the `Data/stream` directory and process each micro-batch of new JSON files, all while the file producer thread remains active.

---

### Cell 8: Code
```python
from bitcoin_utils import run_streaming_query_and_writer
run_streaming_query_and_writer()
```

**Explanation:**
- Imports the `run_streaming_query_and_writer` function.
- Executes it to:
  1. Create a streaming DataFrame that watches the `Data/stream` folder.
  2. Define a `foreachBatch` callback (`process_batch`) that prints count and content of each micro-batch.
  3. Spawn the file producer thread to generate new data.
  4. Run both streaming and producing concurrently for the configured duration.
  5. Gracefully stop the streaming query after completion.

---

### Cell 9: Markdown
**Original Content:**
```markdown
## Displays a preview of the ingested historical Bitcoin price data to verify format and content.
```

**Explanation:**
This cell indicates that the following code will load the accumulated historical data (all JSON lines in `Data/bitcoin_combined.json`) and provide an initial peek—showing a few records and the total count—to validate correct ingestion.

---

### Cell 10: Code
```python
from bitcoin_utils import preview_historical_data
preview_historical_data()
```

**Explanation:**
- Imports `preview_historical_data`.
- Runs the function, which:
  1. Reads the combined JSON history into a Spark DataFrame.
  2. Displays the first five records.
  3. Prints the total number of records—confirming data volume and schema integrity.

---

### Cell 11: Markdown
**Original Content:**
```markdown
## Performs hourly, daily, and rolling window aggregations on Bitcoin price data to analyze trends over time.
```

**Explanation:**
This markdown cell describes three aggregation analyses that will be performed on the historical data to uncover temporal trends: hourly summaries, daily summaries, and a 1‑hour moving average with 30‑minute slides.

---

### Cell 12: Code
```python
from bitcoin_utils import aggregate_hourly_daily_moving_average
aggregate_hourly_daily_moving_average()
```

**Explanation:**
- Imports `aggregate_hourly_daily_moving_average`.
- Executes the function to:
  1. Load and cast the JSON data.
  2. Filter out any null or malformed records.
  3. Group by hour to compute average, minimum, and maximum close prices.
  4. Group by day (YYYY‑MM‑DD) to compute daily summaries.
  5. Compute a rolling 1‑hour moving average with 30-minute slides.
  6. Show the top results for each aggregation in the console.

---

### Cell 13: Markdown
**Original Content:**
```markdown
## Trains a Gradient-Boosted Tree Regressor using PySpark MLlib to predict future Bitcoin prices and evaluates its performance.
```

**Explanation:**
This cell explains that the notebook will next train a machine learning model (Gradient-Boosted Trees) on historical features to forecast future Bitcoin prices, and it will report metrics such as R² and RMSE.

---

### Cell 14: Code
```python
from bitcoin_utils import train_and_evaluate_gbt_regressor
train_and_evaluate_gbt_regressor()
```

**Explanation:**
- Imports the `train_and_evaluate_gbt_regressor` function.
- When called, it:
  1. Constructs new features (`timestamp`, `hour`, `dayofweek`) for modeling.
  2. Assembles these into a feature vector.
  3. Splits data into training and test sets.
  4. Trains a `GBTRegressor` with 100 iterations.
  5. Evaluates model performance (R² and RMSE).
  6. Saves predictions as Parquet, zips results, and optionally uploads to AWS S3 if credentials are provided.

---

### Cell 15: Markdown
**Original Content:**
```markdown
## Generates a time-series plot comparing actual Bitcoin prices against GBT model predictions and saves it as an image.
```

**Explanation:**
This markdown cell introduces the final visualization: plotting real vs. predicted prices over time to visually assess model accuracy and trend capture, and saving the chart as `output_plot.png`.

---

### Cell 16: Code
```python
from bitcoin_utils import plot_actual_vs_predicted_prices
plot_actual_vs_predicted_prices()
```

