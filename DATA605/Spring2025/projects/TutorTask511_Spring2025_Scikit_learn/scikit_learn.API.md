# Scikit-learn API Tutorial

## Overview

In this project, I used the CoinGecko public API to collect historical Bitcoin price data. This data was then used as the basis for training a linear regression model to predict future prices. The API provides access to daily historical price data for a specified number of days.

## API Endpoint

The API endpoint used for fetching the data is:

`https://api.coingecko.com/api/v3/coins/bitcoin/market_chart`

### Parameters

- `vs_currency`: Specifies the currency to compare Bitcoin against. In this case, it is set to 'usd'.
- `days`: The number of past days for which to fetch the historical data.
- `interval`: The frequency of the data. I used 'daily' for this project.

## Steps to Use the API

1. I sent a GET request to the endpoint using the `requests` library in Python.
2. The response is a JSON object containing timestamps and price data.
3. I converted the response into a pandas DataFrame, processed the timestamps into human-readable dates, and used it for model training.

All the above steps are implemented and demonstrated in the `api.ipynb` notebook.
