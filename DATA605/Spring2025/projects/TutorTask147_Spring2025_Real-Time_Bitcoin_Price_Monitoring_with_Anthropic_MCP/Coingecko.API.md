# coingecko.API.py

A lightweight Python client for fetching real‑time and historical Bitcoin data from the CoinGecko API.

## Features

- Get the current Bitcoin price in any currency  
- Fetch OHLC (Open/High/Low/Close) data over a configurable time window  
- Retrieve a historical snapshot (price, market cap, volume) for a specific date  
- Download full market‑chart data (prices, market caps, volumes) for a given number of days  
- Written with clear logging, type hints, and robust error handling  

## Usage
```bash
python coingecko.API.py
```
By default, the script will:

- Log startup information.
- Fetch and log the current BTC price in USD.
- Retrieve 7 days of OHLC data.
- Obtain the BTC price on 2025‑01‑01.
- Download the past 30 days of market‑chart data.

You can import and call individual functions from your own code:
```bash
from coingecko.API import (
    get_bitcoin_price,
    get_coin_ohlc,
    get_historical_data,
    get_market_chart
)

price = get_bitcoin_price("eur")
ohlc  = get_coin_ohlc(days=14)
hist  = get_historical_data(date_str="01-01-2025")
chart = get_market_chart(days=60)
```

## Citations & References
- (CoinGecko API Documentation v3)[https://www.coingecko.com/api/documentations/v3]

- (Causify‑AI Coding Style Guide)[https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md]