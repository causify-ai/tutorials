# 📘 bitcoin_rl_API.md

## Overview

This API notebook demonstrates how to fetch and visualize real-time Bitcoin price data using CoinGecko’s public API, via a custom utility wrapper.

## Function Used

### `fetch_bitcoin_data(vs_currency="usd", days=3)`

- Retrieves timestamped Bitcoin prices
- Converts them to a Pandas DataFrame
- Supports plotting for time-series trend analysis

## Visualization

A time-series plot is generated using `matplotlib`, showing price fluctuations over the last 3 days.

## Output Sample

| Timestamp | Price (USD) |
|-----------|-------------|
| 2025-04-29 00:05:43 | 95023.30 |
| 2025-04-30 01:45:12 | 95581.02 |

