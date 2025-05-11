# Spring2025_s3fs.API.md

## Purpose
This markdown documents the utility function `fetch_bitcoin_data` used to interact with the CoinGecko API and fetch historical Bitcoin prices.

## Function: `fetch_bitcoin_data(api_key: str, days: int = 365, interval: str = 'daily')`
- **Parameters:**
  - `api_key`: CoinGecko API key
  - `days`: Number of days of historical data to fetch
  - `interval`: Data resolution (default: 'daily')
- **Returns:** A Pandas DataFrame with columns:
  - `Timestamp`
  - `Price`

## Usage
The function sends a `GET` request to: https://api.coingecko.com/api/v3/coins/bitcoin/market_chart
...with headers and parameters, parses the JSON, and converts it to a DataFrame.

## Output
Sample:

   Timestamp         Price
0 2024-05-11  60888.216750
1 2024-05-12  60776.972079
2 2024-05-13  61507.054004
3 2024-05-14  62878.783301
4 2024-05-15  61569.113006