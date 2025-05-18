# BitcoinPriceSource API Documentation

This markdown file documents the native API class `BitcoinPriceSource` and the software layer written on top of it, as demonstrated in `XYZ.API.ipynb`.

---

## Overview

`BitcoinPriceSource` is a Python iterable class designed to fetch real-time Bitcoin prices from the CoinGecko API at fixed intervals (default 30 seconds). It maintains a rolling window of recent prices and calculates various statistical metrics such as moving average, standard deviation, exponential moving average, max/min prices, trend, cumulative return, and 24-hour price change.

Additionally, it writes raw price data and computed statistics to an InfluxDB time-series database for further analysis.

---

## How to Use

The class can be instantiated and iterated over in a Python environment. Each iteration yields a tuple `(timestamp, price)` representing the current Unix timestamp (milliseconds) and the latest Bitcoin price in USD.

### Sample usage:

```python
from bitcoin_utils import BitcoinPriceSource

# Create an instance of the source
source = BitcoinPriceSource()

# Iterate to fetch Bitcoin price updates
for i, (timestamp, price) in zip(range(10), source):
    print(f"[{i+1}] Timestamp: {timestamp}, Price: ${price:.2f}") 

## What Happens Internally

- **Fetching Data:** On each iteration, the API queries CoinGecko for the latest Bitcoin price and 24h percent change.

- **Rolling Window:** Maintains a fixed-size window (default 10 samples) of recent prices.

- **Metrics Calculation:** Once enough data points are collected, calculates:

  - Moving Average (MA)

  - Standard Deviation (StdDev)

  - Exponential Moving Average (EMA)

  - Max and Min prices

  - Trend indicator (`1` for upward trend, `-1` for downward)

  - Cumulative return over the window

  - 24-hour percent price change

- **Data Storage:** Writes raw and computed data to InfluxDB for persistent storage.

- **Logging:** Prints the fetched prices and metrics to the console.

---

## Summary

`BitcoinPriceSource` abstracts real-time Bitcoin price streaming with integrated statistics and time-series storage. The API is easy to integrate with Python iterables and provides valuable insights for downstream analysis or visualization.

The companion Jupyter notebook `XYZ.API.ipynb` demonstrates minimal, clean usage of this API layer.
