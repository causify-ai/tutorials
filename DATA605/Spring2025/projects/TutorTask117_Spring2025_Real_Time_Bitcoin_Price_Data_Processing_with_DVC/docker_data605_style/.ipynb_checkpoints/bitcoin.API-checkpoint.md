#  bitcoin.API.md  
**Module:** `bitcoin.API.ipynb`  
**Author:** Shruti Gajipara 
**Project:** Real-Time Bitcoin Data Processing with DVC  

---

## Overview

This notebook demonstrates the usage of a custom Python API wrapper (`bitcoin_utils.py`) to perform real-time Bitcoin price monitoring and analysis. It provides a clean interface to fetch live BTC prices, store them with timestamps, perform basic time series analysis, and visualize the trends — all using open-source tools and integrated into a reproducible DVC pipeline.

---

##  Architecture

The notebook uses the following Python modules:

- `bitcoin_utils.py`: Wrapper around 3 core modules:
  - `src/live_fetcher.py`: Fetches live price via CoinGecko API
  - `src/data_ingestion.py`: Records prices into CSV
  - `src/preprocess_eda.py`: Adds rolling average, computes deltas, plots data

**Core Flow:**
fetch_price() → record_price() → preprocess() → plot_data()

##  Features Demonstrated

###  Live Data Capture
- Records the live Bitcoin price every 10 seconds for 2 minutes (12 entries)
- Each entry includes a full timestamp and is saved to `data/bitcoin_prices.csv`

###  Timestamp-Aware Logging
- Each recorded price is formatted as:  
  “On Tuesday, May 21, 2025 at 12:44 PM UTC, the Bitcoin price was $64,123.87”

###  Preprocessing Pipeline
- Automatically adds:
  - `price_diff`: Change since last entry
  - `rolling_avg`: Smoothed trend using a 5-point moving average
- Cleaned data is saved to `data/cleaned_bitcoin.csv`

###  Visualizations
- Line chart of raw prices (`plot_data`)
- Dual-line plot showing:
  - Price change spikes (Δ)
  - Rolling average trend

###  Summary Stats
- Displays key descriptive statistics for price, difference, and trend

###  Formatted Tables
- Tables for:
  - Last 12 recorded entries (2-minute loop)
  - BTC prices in last 30 minutes (if available)
- All timestamps are human-readable (Day, Date, Time)

---

##  Files Used

| File | Purpose |
|------|---------|
| `bitcoin_utils.py` | Main API wrapper |
| `data/bitcoin_prices.csv` | Raw log of prices |
| `data/cleaned_bitcoin.csv` | Processed data |
| `Output/bitcoin_price_plot.png` | Auto-generated plot |
| `bitcoin.API.ipynb` | This notebook |
| `bitcoin.API.md` | This documentation |

---

##  Dependencies
pandas
requests
matplotlib
dvc

##  Notes

- This notebook is designed to be self-contained.
- All functions are imported from the utils module for cleaner cells.
- API failures (e.g., CoinGecko rate limits) are handled gracefully.
- Final output is suitable for embedding in reports or real-time dashboards.


