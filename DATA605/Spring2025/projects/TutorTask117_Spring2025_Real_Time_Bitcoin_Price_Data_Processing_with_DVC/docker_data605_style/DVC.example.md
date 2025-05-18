# 📘 DVC.example.md

## Overview

This notebook demonstrates a full real-time pipeline for fetching, processing, and analyzing Bitcoin price data using DVC.

It integrates live data collection, preprocessing, visualization, and reproducible pipeline tracking using the `bitcoin_utils.py` module.

---

## Pipeline Flow

### 1. Live Data Recording

- Uses CoinGecko API to fetch real-time BTC prices every 10 seconds for 2 minutes.
- Data is stored with UTC timestamps in `data/bitcoin_prices.csv`.

### 2. Raw Data Viewing

- Displays the latest rows of raw recorded prices.
- Timestamps are parsed and cleaned.

### 3. Preprocessing

- Computes:
  - `price_diff`: change between consecutive prices
  - `rolling_avg`: 5-point rolling average
- Outputs saved to `data/cleaned_bitcoin.csv`.

### 4. Visualizations

The following plots are generated:

- Line chart with actual price and 10-point rolling average
- Histogram showing price distribution with mean and median
- Volatility band (±1 std dev around 7-point average)
- Price difference bar plot
- Box plot of price values
- Combined chart of price + rolling + diff

Saved to `Output/` folder as `.png`.

### 5. Summary Statistics

- Displays `describe()` statistics for price, difference, and trend
- Saves final output as Excel: `Output/final_bitcoin_data.xlsx`

### 6. DVC Check

- Confirms tracked files using `!dvc status`
- Ensures the pipeline remains reproducible and versioned

---

## File Outputs

| File                              | Description                            |
|-----------------------------------|----------------------------------------|
| `data/bitcoin_prices.csv`         | Raw recorded BTC prices                |
| `data/cleaned_bitcoin.csv`        | Cleaned + feature-enhanced data        |
| `Output/bitcoin_price_plot.png`   | Final plotted chart                    |
| `Output/final_bitcoin_data.xlsx`  | Cleaned data in Excel format           |

---

## Notes

- Run this notebook top-to-bottom for full execution.
- Requires DVC and Python packages defined in `requirements.txt`.
- Imports core logic from `bitcoin_utils.py`.

