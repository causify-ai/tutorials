<!-- toc -->

- [txtai API Tutorial](#txtai-api-tutorial)
  * [Table of Contents](#table-of-contents)
  * [Overview](#overview)
  * [Key Functions](#key-functions)
    + [fetch_bitcoin_headlines(api_key)](#fetch_bitcoin_headlines)
    + [analyze_sentiment(headline)](#analyze_sentiment)
    + [fetch_bitcoin_prices(days=30)](#fetch_bitcoin_prices)
    + [merge_sentiment_and_price(df_sentiment, df_prices)](#merge_sentiment_and_price)
  * [Environment Notes](#environment-notes)
  * [Logging](#logging)

<!-- tocstop -->

# txtai API Tutorial

## Table of Contents

This markdown documents the API functions implemented in `txtai_utils.py` to support real-time Bitcoin sentiment analysis using semantic embeddings.

---

## Overview

The `txtai_utils.py` module provides utility functions for:
- Fetching Bitcoin-related news headlines from NewsAPI
- Analyzing sentiment using `txtai` embeddings
- Fetching historical Bitcoin prices from CoinGecko
- Aligning and merging sentiment and market data

These APIs are used by the `txtai.API.ipynb` notebook to produce visual insights and forecasts.

---

## Key Functions

### fetch_bitcoin_headlines

Fetches top Bitcoin-related news headlines from NewsAPI.

- **Returns**: `List[str]` of headlines.
- **Usage**:
```python
headlines = fetch_bitcoin_headlines(API_KEY)
```
### analyze_sentiment

Scores a given headline using a pretrained `txtai` sentiment model.

- **Returns**: `Tuple[str, float]` → label (`POSITIVE` / `NEGATIVE`) and confidence  
- **Usage**:
```python
label, score = analyze_sentiment("Bitcoin hits new high")
```
### fetch_bitcoin_prices(days=30)

Retrieves daily historical Bitcoin prices using the CoinGecko API.
- **Returns**: `pandas.DataFrame` with columns `date` and `price`.
- **Usage**:
```python
df_prices = fetch_bitcoin_prices(days=30)
```
### merge_sentiment_and_price
         
Combines sentiment data with Bitcoin price data by matching dates.
- **Returns**: Merged `DataFrame` with sentiment, headline, and price columns.

---
    
## Environment Notes
These functions are written for flexible use in both:

- Jupyter notebooks (interactive analysis)

- Dockerized environments with API key access

No authentication is needed for CoinGecko. A valid API key is required for NewsAPI.

---
                                            
## Logging
Functions print informative messages using Python’s `logging` module:

- `INFO` level is used for data fetches, sentiment analysis, etc.

- `ERROR` level will show in case of failed API calls or missing values

This allows traceability when running inside container logs.