# stablebaseline3.API.md

## Purpose

This document describes the native CoinGecko API used in our project and the utility layer we created around it inside `stablebaseline3_utils.py`. The goal was to simplify real-time and historical Bitcoin data fetching for seamless integration with the Stable-Baselines3 reinforcement learning pipeline.

---

## Native API Overview

We use the free public [CoinGecko API](https://www.coingecko.com/en/api) to fetch Bitcoin price data.

### Key Endpoints:
- `/simple/price`: Provides current market price of Bitcoin in a specified currency.
- `/coins/bitcoin/market_chart`: Returns historical price data (hourly or daily).

### Example (Native Call):
```python
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
response = requests.get(url)
btc_price = response.json()["bitcoin"]["usd"]
