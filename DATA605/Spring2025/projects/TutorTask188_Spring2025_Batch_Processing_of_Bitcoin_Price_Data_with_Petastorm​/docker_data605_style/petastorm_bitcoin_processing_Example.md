
## Batch Processing of Bitcoin Price Data with Petastorm

<!-- toc -->

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
  * [Data Ingestion](#1-data-ingestion)
  * [Batch Data Storage](#2-batch-data-storage)
  * [Data Processing & Analysis](#3-data-processing--analysis)
  * [Machine Learning Model](#4-machine-learning-model)
- [Key Components](#key-components)
- [Utils](#utils)
- [How to run the notebook](#how-to-run-the-notebook)
<!-- tocstop -->

## Introduction

Welcome to this project! This document serves as a comprehensive guide to help you get started quickly. It provides:

- A clear overview of the repository’s purpose and scope.  
- Descriptions of the key modules and files you’ll encounter.  
- Step-by-step examples demonstrating how to run the code and integrate it into your own projects.

By following this README, you’ll gain a solid understanding of the project structure and learn how to leverage its components effectively.

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

### 3. **Data Processing & Analysis**
- Parquet files are read using **Petastorm's `make_batch_reader()`**.
- Data is converted to Pandas DataFrames for analysis.
- Time series operations such as **moving average calculation**, **volatility**, or **trend detection** are applied.
- Processed Parquet data is used to train forecasting models using **TensorFlow** or **PyTorch**.
- Historical price data can be modeled for **regression** or **sequence prediction** tasks.

### 4. **Machine Learning Model**
- A stacked LSTM model is used for time-series forecasting of Bitcoin prices.
- Visual plots generated using Matplotlib to display:
  - Raw price over time  
  - Moving averages  
  - Forecast vs. actual trends  


## Key Components

This project is organized into the following core components:

1. **Data Ingestion**  
   - Scripts and utilities to fetch raw Bitcoin price data from external APIs (e.g., CoinGecko).  
   - Automated routines for scheduling periodic data retrieval and initial validation.

2. **Data Storage**  
   - Conversion of raw CSV data into Parquet format for efficient storage.  
   - Petastorm-compatible dataset layout enabling parallel reads and metadata management.

3. **Data Processing and Analysis**  
   - ETL pipelines to clean, normalize, and merge incoming data streams.  
   - Exploratory analysis notebooks demonstrating aggregation, time-series resampling, and statistical summaries.

4. **Machine Learning Model**  
   - Pre-built LSTM/forecasting models configured for Bitcoin price prediction.  
   - Training scripts with hyperparameter tuning examples and model checkpointing.

5. **Insights and Graphs from Example**  
   - Visualization modules generating plots for price trends, volatility metrics, and forecasting accuracy.  
   - Dashboards showcasing interactive charts and summary statistics for end-to-end demonstration.

## Machine Learning Model Used

### LSTM Model Description

The notebook uses a stacked LSTM architecture for time-series forecasting:

- **Layer 1**:  
  `tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(look_back, 1))`

- **Dropout**:  
  `tf.keras.layers.Dropout(0.2)`

- **Layer 2**:  
  `tf.keras.layers.LSTM(50, return_sequences=False)`

- **Dropout**:  
  `tf.keras.layers.Dropout(0.2)`

- **Output**:  
  `tf.keras.layers.Dense(1)`

Compiled with MSE loss and the Adam optimizer. EarlyStopping and ModelCheckpoint callbacks are used during training to retain the best model.

## Utils
The `utils.py` file provides a comprehensive suite of helper functions for fetching, storing, processing, and visualizing Bitcoin price data, as well as integrating a stacked LSTM forecasting model.

### Data Ingestion

- **fetch_current_price(base_url)**  
  Fetches the current Bitcoin price, market cap, and 24 h price change in USD from the CoinGecko API and returns a dict with `timestamp`, `price_usd`, `market_cap`, and `price_change_24h`.

### Data Storage

- **save_to_csv(df, output_dir, filename=None)**  
  Saves a Pandas DataFrame to a CSV file in the specified directory (auto-generating a timestamped filename if none is given) and returns the full file path.

- **save_to_parquet_arrow(df, output_path="file:///…/parquet")**  
  Converts a Pandas DataFrame into a PyArrow Table and writes it as `data.parquet` in the given directory—creating the folder if needed—for Petastorm compatibility.

### Data Processing

- **load_all_csvs_from_folder(folder_path)**  
  Reads all `.csv` files in a folder, concatenates them into one DataFrame (ignoring load errors), and returns the combined DataFrame (or an empty one if no CSVs found).

- **load_petastorm_batches_to_df(parquet_path)**  
  Uses Petastorm’s batch reader to iterate over all record batches in a Parquet dataset and concatenates them into a single Pandas DataFrame.

- **load_from_parquet(input_dir)**  
  Generator that yields successive batches from a Petastorm-compatible Parquet directory, normalizing `file://` paths as needed.

- **get_parquet_columns(parquet_file_path)**  
  Reads a Parquet file via PyArrow and returns its list of column names.

- **prepare_bitcoin_df(df)**  
  Ensures the DataFrame has `timestamp` and `price_usd` columns, parses timestamps, drops invalid rows, sets `timestamp` as sorted index, and returns the cleaned DataFrame.

- **calculate_moving_average(df, window=7)**  
  Computes a rolling moving average of `price_usd` over the specified window (default 7), adds it as `ma_<window>`, and returns the augmented DataFrame.

- **calculate_volatility(df, window=7)**  
  Calculates rolling standard deviation of the percentage change in `price_usd` over the given window (default 7), adds it as `volatility_<window>`, and returns the DataFrame.

### ML Integration & Visualization

- **plot_price_trend(df)**  
  Plots the time series of `price_usd` (and `ma_7` if present) using Matplotlib, labeling axes, adding a legend and grid.

- **plot_volatility(df)**  
  Ensures `volatility_7` exists (computing it if necessary) and then plots the 7-day volatility series with titles and grid.

- **generate_report(df)**  
  Runs `calculate_moving_average` and `calculate_volatility`, prints summary statistics (time period, count, price describe, latest price and 24 h change), and calls `plot_price_trend` and `plot_volatility` to visualize the results.


## How to run the notebook:

1. Clone the repository to your local machine and then change into that directory.

2. Install all required Python packages by running pip install -r requirements.txt.

3. Launch Jupyter by typing jupyter notebook or jupyter lab in your terminal.

4. In the browser window that opens, locate and open the file named petastorm_bitcoin_processing_Example.ipynb.

5. If any file paths are hard-coded in the notebook (for example, where it looks for your Parquet or CSV files), update them at the top to match your local directories.

6. From the menu choose Kernel → Restart & Run All so that every cell executes in sequence. This will ingest and preprocess the data, build and train the stacked LSTM model, and generate the plots and summary statistics.

7. When it finishes, review the charts and printed metrics in the notebook, and find any saved model checkpoints in the checkpoints/ folder.