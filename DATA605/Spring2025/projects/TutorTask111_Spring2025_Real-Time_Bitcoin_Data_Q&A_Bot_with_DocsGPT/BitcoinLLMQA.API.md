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

All core logic resides in `BitcoinLLMQA_utils.py` and is demonstrated in `BitcoinLLMQA.API.ipynb`.

---

## Table of Contents

### Hierarchy

Level 1 (Title)
Level 2
Level 3
text

---

## General Guidelines

- Documents both native API (CoinGecko) and wrapper layer
- All functions reusable in scripts/notebooks
- Example usage shown in `BitcoinLLMQA.API.ipynb`

---

## Native API

### CoinGecko Simple Price API

Direct API call from notebook
response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")

text

| Parameter       | Value                          |
|-----------------|--------------------------------|
| Endpoint        | `GET /simple/price`            |
| Authentication  | None required                  |
| Rate Limits     | 50 calls/minute (free tier)    |
| Sample Response | `{"bitcoin": {"usd": 103272}}` |

---

## Software Wrapper Layer

### Data Fetching

def fetch_bitcoin_price() -> float | None

text
- Fetches current BTC price via CoinGecko API
- Implements retry logic for failed requests
- Returns `None` on persistent failures

### Dataset Update

def update_dataset(new_price: float) -> pd.DataFrame

text
- Appends records to `bitcoin_prices.csv` with:
  - ISO 8601 timestamps
  - Rolling volatility (12-period window)
  - Log returns calculation
- Maintains dataset integrity through file locking

### Data Loading

def load_dataset(filename=CSV_FILENAME) -> pd.DataFrame

text
- Loads CSV with dtype optimization:
  - `timestamp` as datetime64[ns]
  - `price` as float32
  - `volatility` as float32
- Handles missing values via forward-fill

### Time Series Analysis

def analyze_data(df: pd.DataFrame) -> dict

text
Returns structured metrics:
{
"hourly_avg": {
"price": 29623.30,
"volatility": 0.252296
},
"daily_volatility": 0.241686,
"recent_anomalies": [
["2025-05-09 21:17:00", 31924.06, 0.254599]
]
}

text

### Visualization

def visualize_bitcoin_data(df: pd.DataFrame, periods=48)

text
- Generates dual-axis plot using matplotlib
- Left axis: Price in USD
- Right axis: Rolling volatility percentage
- Saves figures to `plots/` directory

### Price Trend Analysis

def get_price_trends(df: pd.DataFrame, period='24h') -> dict

text
Supports periods:
- `1h`, `24h`, `7d`, `30d`
- Returns % changes, max/min values, and volatility trends

---

## LLM Q&A Integration (DocsGPT/LLaMA)

### Model Setup

def setup_docsgpt() -> Llama

text
- Loads 7B LLaMA 2 GGUF model
- Configures GPU layers for acceleration
- Sets 2048 token context window

### Natural Language Query

def handle_query(llm: Llama, question: str) -> str

text
- Combines user question with:
  - Last 10 data rows
  - Current volatility status
  - Price trend metrics
- Uses chain-of-thought prompting for accurate responses

---

## Example Usage

Full workflow from notebook
price = fetch_bitcoin_price() # Returns 103272.0
df = update_dataset(price)
metrics = analyze_data(df)
fig = visualize_bitcoin_data(df)
llm = setup_docsgpt()
answer = handle_query(llm, "Show volatility spikes in last 6 hours")

text

---

## Design Decisions

| Component          | Implementation Choice         | Reason                          |
|--------------------|-------------------------------|---------------------------------|
| Data Storage       | CSV with timestamps           | Human-readable/portable         |
| Volatility Window  | 12-period (1 hour)            | Balances responsiveness/stability |
| LLM Context        | Last 10 rows + stats          | Optimizes token usage           |
| Error Handling     | Silent fails with NaN         | Maintains data continuity       |

---

## References

1. [CoinGecko API Docs](https://www.coingecko.com/en/api)
2. [DocsGPT GitHub](https://github.com/arc53/DocsGPT) 
3. [Pandas Time Series Guide](https://pandas.pydata.org/docs/user_guide/timeseries.html)

**Last updated:** May 10, 2025