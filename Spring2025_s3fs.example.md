# Spring2025_s3fs.example.md

## Overview
This example demonstrates a full Final-project using `s3fs` and Python for time series analysis of Bitcoin prices.

## Objective
- Fetch real-time Bitcoin prices from CoinGecko API
- Store the results locally and (optionally) on S3
- Analyze and visualize price trends, seasonality, and volatility

## Steps

### 1. Fetch Data
We use the utility function `fetch_bitcoin_data` to pull 1 year of daily Bitcoin prices.

### 2. Save CSV
The data is saved as `bitcoin_prices.csv`.

### 3. Decomposition
We decompose the time series into:
- **Trend**
- **Seasonality**
- **Residuals**

### 4. Moving Average
A 5-day moving average is computed to observe smoothed patterns.

### 5. Visualization
Matplotlib is used to generate:
- Line chart of daily prices
- Decomposed view
- Overlay of price vs. 5-day moving average

### 6. Optional Upload to S3
We demonstrate writing CSV back to Amazon S3 using `s3fs`. Credentials must be mounted locally and AWS CLI configured.

---

## Final Outcome
A reproducible project that showcases:
- API integration
- Cloud storage with `s3fs`
- Trend detection using time series techniques

## Tools Used
- Python, Pandas, Statsmodels, s3fs, Matplotlib
