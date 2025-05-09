<!-- toc -->

- [BitcoinLLMQA API Documentation](#bitcoinllmqa-api-documentation)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
    - [Hierarchy](#hierarchy)
  - [General Guidelines](#general-guidelines)
  - [Native API](#native-api)
    - [CoinGecko Simple Price API](#coingecko-simple-price-api)
  - [Software Wrapper Layer](#software-wrapper-layer)
    - [Data Fetching](#data-fetching)
    - [Dataset Update](#dataset-update)
    - [Data Loading](#data-loading)
    - [Time Series Analysis](#time-series-analysis)
    - [Visualization](#visualization)
    - [Price Trend Analysis](#price-trend-analysis)
  - [LLM Q\&A Integration (DocsGPT/LLaMA)](#llm-qa-integration-docsgptllama)
    - [Model Setup](#model-setup)
    - [Natural Language Query](#natural-language-query)
  - [Example Usage](#example-usage)
  - [Design Decisions](#design-decisions)
  - [References](#references)

<!-- tocstop -->

# BitcoinLLMQA API Documentation

## Overview

**BitcoinLLMQA** is a real-time Bitcoin price data Q&A system combining:
- **CoinGecko API** for BTC/USD market prices  
- **Pandas** for time series analysis  
- **DocsGPT (LLaMA)** for local, offline question answering  

All core logic resides in `BitcoinLLMQA_utils.py` and is reusable via Python scripts or Jupyter notebooks.

---

## Table of Contents

See the TOC above for all sections and subsections.

### Hierarchy

Level 1 (Used as title)
Level 2
Level 3
text

---

## General Guidelines

- This file documents both the native API (CoinGecko) and the software wrapper layer in `BitcoinLLMQA_utils.py`.
- All API usage is demonstrated in `BitcoinLLMQA.API.ipynb`.
- The wrapper functions are designed for reuse in notebooks and scripts.

---

## Native API

### CoinGecko Simple Price API

- **Endpoint:**  
  `GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`

- **Authentication:**  
  Not required

- **Rate Limits:**  
  ~50 requests per minute (free tier)

- **Sample Response:**
{
"bitcoin": {
"usd": 101160
}
}

text

---

## Software Wrapper Layer

All wrappers are in `BitcoinLLMQA_utils.py`.

### Data Fetching

def fetch_bitcoin_price() -> float | None

text
Fetches the current Bitcoin price (USD) from CoinGecko.  
Returns `None` if the API call fails.

---

### Dataset Update

def update_dataset(new_price: float) -> pd.DataFrame

text
Appends a new price record (with timestamp) to `bitcoin_prices.csv` and recalculates rolling volatility (1-hour window, 12x5min intervals).

---

### Data Loading

def load_dataset(filename=CSV_FILENAME) -> pd.DataFrame

text
Loads the CSV dataset, parses timestamps, and ensures correct types.

---

### Time Series Analysis

def analyze_data(df: pd.DataFrame) -> dict

text
Returns:
- `hourly_avg`: Hourly price and volatility averages
- `daily_volatility`: Daily volatility
- `recent_anomalies`: Rows where volatility exceeds the 95th percentile

---

### Visualization

def visualize_bitcoin_data(df: pd.DataFrame, periods=48) -> matplotlib.figure.Figure

text
Plots price and rolling volatility for the last N records.

---

### Price Trend Analysis

def get_price_trends(df: pd.DataFrame, period='24h') -> dict

text
Calculates price change, max/min, and percent change over the specified period (`'24h'`, `'7d'`, etc.).

---

## LLM Q&A Integration (DocsGPT/LLaMA)

### Model Setup

def setup_docsgpt() -> Llama

text
Loads the LLaMA model for local inference.

---

### Natural Language Query

def handle_query(llm: Llama, question: str) -> str

text
Processes a natural language question using the LLaMA model and returns a plain-English answer.  
Context can be added to the prompt for more accurate results.

---

## Example Usage

Fetch and store data
price = fetch_bitcoin_price()
df = update_dataset(price)

Analyze and visualize
metrics = analyze_data(df)
fig = visualize_bitcoin_data(df)
fig.show()

Q&A
llm = setup_docsgpt()
answer = handle_query(llm, "What was the highest price in the last 6 hours?")
print(answer)

text

---

## Design Decisions

- **Rolling Volatility:** 12-period window (1 hour at 5-min intervals) for short-term risk analytics.
- **CSV Storage:** Simple, portable, and easy to inspect.
- **LLM Integration:** Local LLaMA model for privacy and offline Q&A.
- **All logic in utils.py:** Ensures maintainability and reusability.

---

## References

- [CoinGecko API Documentation](https://www.coingecko.com/en/api)
- [DocsGPT GitHub](https://github.com/arc53/DocsGPT)
- [Pandas Time Series Guide](https://pandas.pydata.org/docs/user_guide/timeseries.html)

---

**Last updated:** May 8, 2025