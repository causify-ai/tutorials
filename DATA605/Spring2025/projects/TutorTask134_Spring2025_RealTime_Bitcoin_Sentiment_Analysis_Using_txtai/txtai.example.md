<!-- toc -->

- [Project Title](#project-title)
  * [Table of Contents](#table-of-contents)
  * [Overview](#overview)
  * [Architecture](#architecture)
  * [Workflow](#workflow)
  * [Technologies Used](#technologies-used)
  * [References](#references)

<!-- tocstop -->

# Project Title

Real-Time Bitcoin Sentiment Analysis using `txtai`

## Table of Contents

This markdown explains how the `txtai_utils.py` API functions are used in a real-world sentiment analysis pipeline.

---

## Overview

This project uses `txtai`, `NewsAPI`, and `CoinGecko` to:
- Fetch live Bitcoin-related headlines
- Score them using semantic embeddings
- Merge the sentiment with market data
- Visualize and forecast short-term price movement using ARIMA

It is implemented in a single Dockerized Jupyter notebook environment.

---

## Architecture

- **Data Sources**:
  - NewsAPI for real-time headlines
  - CoinGecko API for daily price data

- **Modules**:
  - `txtai_utils.py` for all helper functions
  - `txtai.API.ipynb` for full execution flow

- **Environment**:
  - Docker container with Python 3.9+
  - Jupyter notebook UI for results and charts

---

## Workflow

The notebook `txtai.API.ipynb` performs the following:

1. **Fetch News Headlines**  
   - Uses `fetch_bitcoin_headlines()` to retrieve up to 100 headlines.

2. **Analyze Sentiment**  
   - Applies `analyze_sentiment()` using `txtai` to classify as POSITIVE or NEGATIVE.

3. **Fetch Bitcoin Prices**  
   - Uses `fetch_bitcoin_prices()` to collect daily historical values for comparison.

4. **Merge Data**  
   - Aligns by `date` using `merge_sentiment_and_price()`.

5. **Visualize and Forecast**  
   - Produces:
     - Line chart of historical price
     - Bar chart of sentiment per day
     - 7-day ARIMA forecast of price

---

## Technologies Used

- Python 3.9+
- txtai
- NewsAPI
- CoinGecko API
- Statsmodels
- Pandas, Matplotlib, Seaborn
- Docker
---

## References

- [`txtai_utils.py`](./code/txtai_utils.py): function definitions
- [`txtai.API.ipynb`](./code/txtai.API.ipynb):full implementation notebook
- [`txtai`](https://github.com/neuml/txtai)
- [NewsAPI](https://newsapi.org/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Statsmodels Docs](https://www.statsmodels.org/)