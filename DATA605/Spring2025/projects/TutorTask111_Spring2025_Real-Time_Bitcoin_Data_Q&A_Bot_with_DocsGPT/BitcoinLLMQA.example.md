<!-- toc -->

- [Project Title: BitcoinLLMQA](#project-title-bitcoinllmqa)
  - [Table of Contents](#table-of-contents)
    - [Hierarchy](#hierarchy)
  - [General Guidelines](#general-guidelines)
  - [Architecture Overview](#architecture-overview)
  - [Technologies Used](#technologies-used)
  - [Data Pipeline](#data-pipeline)
  - [Functionality Demonstrated](#functionality-demonstrated)
  - [Sample Queries](#sample-queries)
  - [LLM Integration Design](#llm-integration-design)
  - [Conclusion](#conclusion)

<!-- tocstop -->

# Project Title: BitcoinLLMQA

**BitcoinLLMQA** is a real-time Bitcoin price analysis and natural language query system built using:
- The CoinGecko API for live BTC/USD price retrieval
- A custom Python wrapper layer for time-series tracking and volatility analysis
- A local LLaMA model (DocsGPT) for question-answering over recent price data

## Table of Contents

This markdown includes a Table of Contents (TOC) using `Markdown All in One`.

### Hierarchy

Markdown structure follows:

Level 1 (Used as title)
Level 2
Level 3


**Note** Level 1 Heading (Title) should be `Project Title`

## General Guidelines

- Based on [README](/DATA605/DATA605_Spring2025/README.md) structure and API integration requirements.
- Demonstrates integration of a native API (CoinGecko) via reusable wrappers.
- Corresponding code and examples shown in `BitcoinLLMQA.example.ipynb`.

---

## Architecture Overview

[ CoinGecko API ]
↓
[ fetch_bitcoin_price() ]
↓
[ update_dataset() → CSV ]
↓
[ analyze_data(), visualize_bitcoin_data() ]
↓
[ DocsGPT + handle_query() ← user questions ]



- The system runs a 5-minute loop for price polling and CSV updating.
- Volatility is calculated using rolling log returns.
- DocsGPT provides LLM-based Q&A over recent data snapshots.

---

## Technologies Used

| Component       | Tool/Library                |
|----------------|-----------------------------|
| API             | CoinGecko Public API        |
| Language        | Python 3.12 (Conda base env)|
| Data Handling   | Pandas, NumPy               |
| Visualization   | Matplotlib                  |
| LLM Model       | LLaMA via `llama-cpp-python`|
| Q&A Layer       | DocsGPT (locally deployed)  |

---

## Data Pipeline

1. **Price Fetch** – CoinGecko API called via `requests`
2. **Timestamped Record** – Appended to `bitcoin_prices.csv`
3. **Volatility Computation** – Rolling std dev of log returns (12-point = 1 hour)
4. **Time-Based Aggregation** – Hourly/daily summaries via `resample()`
5. **DocsGPT Query Context** – Last 10 rows used as prompt input

---

## Functionality Demonstrated

- Real-time data ingestion
- CSV-based tracking and analysis
- Visualization of price + volatility
- Query answering with LLaMA:
  - Maximum price
  - Drop percentage
  - Volatility spikes

---

## Sample Queries

> What was the highest Bitcoin price today?  
> When did the price drop more than 2%?  
> Show the average volatility this week.

---

## LLM Integration Design

- `setup_docsgpt()` loads a local `.gguf` LLaMA model with constrained context size (2048 tokens)
- `handle_query()` creates a formatted prompt combining user question and latest dataset rows
- Uses local resources for inference (no OpenAI key required)
- Ensures privacy and offline usability

---

## Conclusion

**BitcoinLLMQA** demonstrates how real-time financial data can be:
- Captured and stored efficiently
- Analyzed through statistical techniques
- Queried using natural language via offline LLMs

The modular utility structure ensures future extensibility, e.g., to ETH or NASDAQ data or new LLM models.

