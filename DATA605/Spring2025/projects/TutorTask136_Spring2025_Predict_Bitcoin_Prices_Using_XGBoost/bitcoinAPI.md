<!-- toc -->

- [Bitcoin_xgboost API](#bitcoin_xgboost-api)
  * [Description](#description)
  * [References](#references)
  * [Import Dependencies](#import-dependencies)
  * [Download Historical Bitcoin Data (Yahoo Finance)](#download-historical-bitcoin-data-yahoo-finance)
    + [Visualize Yahoo Finance Data](#visualize-yahoo-finance-data)
    + [Yahoo Finance Data Characteristics](#yahoo-finance-data-characteristics)
  * [Fetch Real-Time Historical Data (CoinGecko API)](#fetch-real-time-historical-data-coingecko-api)
    + [Visualize CoinGecko Data](#visualize-coingecko-data)
    + [CoinGecko Data Characteristics](#coingecko-data-characteristics)
  * [Compare Data Structures](#compare-data-structures)
  * [Summary](#summary)

<!-- tocstop -->

# Bitcoin_xgboost API

## Description

This module provides functions to download and process Bitcoin price data from two popular sources:

- **Yahoo Finance:** Offers long-term historical Bitcoin data (nearly 10 years).
- **CoinGecko API:** Provides recent historical data (last 365 days).

The API enables data retrieval, visualization, and comparison for financial modeling and analysis purposes.

## References

- [`temple.API.md`](./temple.API.md)  
- [CoinGecko API Documentation](https://www.coingecko.com/en/api)  
- [Yahoo Finance via yfinance](https://pypi.org/project/yfinance/)  
- [Causify AI Notebook Guide](https://github.com/causify-ai/helpers/blob/master/docs/coding/all.jupyter_notebook.how_to_guide.md)  

---

## Import Dependencies

The API requires the following Python packages:

```python
import pandas as pd
import matplotlib.pyplot as plt
from bitcoin_utils import download_crypto_data, fetch_historical_bitcoin
