<!-- toc -->

- [Introduction](#introduction)
  * [Key Components](#key-components)
    + [1. BitcoinAPI](#1-bitcoinapi)
      - [Key Features:](#key-features)
      - [Example:](#example)
  * [Complete Workflow](#complete-workflow)
  * [Example Usage](#example-usage)

<!-- tocstop -->

# Introduction

This module provides a simple Python class `BitcoinAPI` to fetch real-time Bitcoin price data using the CoinGecko API. It encapsulates the API call, error handling, and response formatting into a reusable function. The script is intended to be run in a loop to periodically collect data.

## Key Components

### 1. BitcoinAPI

The `BitcoinAPI` class is a utility wrapper around the CoinGecko `/simple/price` endpoint. It fetches Bitcoin’s current price in USD along with the 24-hour trading volume.

#### Key Features:

- **Lightweight and Stateless**:
  - Makes a GET request to the CoinGecko API to fetch the current price and volume of Bitcoin in USD.
  - Designed to be stateless and reusable for multiple periodic calls.
  
- **Error Handling**:
  - Gracefully handles API failures using `try-except`.
  - Logs failures using Python’s built-in `logging` module.

- **Timestamped Output**:
  - Attaches a Unix timestamp to every record to support downstream time series analytics.

- **Logging Enabled**:
  - Uses `_LOG.info()` and `_LOG.error()` to provide traceable logs, replacing raw `print()` calls.


## Process Flowchart

![geckp_api_flow](https://github.com/user-attachments/assets/a42a1580-5d08-409a-8409-7cc75ca67ea1)

#### Example:

```python
api = BitcoinAPI()
result = api.fetch_bitcoin_price()
print(result)


#The output will return like

{
    'timestamp': 1747459847,
    'price': 103559.0,
    'currency': 'USD',
    'volume': 25412480008.35425
}

