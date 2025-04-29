<!-- toc -->

- [Project Title](#project-title)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)

<!-- tocstop -->

# Project Title

Building a real-time data ingestion, storage, and analysis pipeline for Bitcoin prices using **Snowflake**, **CoinGecko API**, and a modular Python API layer (`snowflake_utils.py`).

This system enables users to:
- Load historical Bitcoin price data (last 90 days)
- Ingest live Bitcoin price data regularly
- Store and retrieve data efficiently using Snowflake
- Analyze and visualize time-series trends (moving average, volatility)

---

## Table of Contents

This markdown file documents the end-to-end implementation for the project:
- Initial data loading and ingestion design
- Use of utility APIs in a pipeline
- Sample analysis and visualization components
- Integration into dashboards and notebooks

---

### Hierarchy

```
# Level 1 (Used as title)
All the subheadings should follow the below structure:
## Level 2
### Level 3
```

---

## General Guidelines

- This project follows the submission conventions of DATA605 Spring 2025.
- The system demonstrates how to use the reusable functions from `bitcoin_utils.py` in a real-world context.
- The entire demonstration is implemented in [`bitcoin.example.ipynb`](./bitcoin.example.ipynb) and is fully executable from top to bottom.

### Architecture

- **Source**: CoinGecko REST API (public)
- **Destination**: Snowflake table `bitcoin_prices` inside `btc_db.public`
- **Tools**: Python, pandas, Streamlit, Snowflake Connector, Docker

### Data Flow

1. `load_historical_prices_to_snowflake()` fetches and loads last 90 days of BTC prices into Snowflake
2. `fetch_bitcoin_price()` retrieves the latest price
3. `insert_price_to_snowflake()` loads this record into the same table
4. `query_all_prices()` extracts the full price history into a DataFrame
5. The notebook visualizes this using Matplotlib

### Usage

The example notebook showcases:
- 7-day moving averages
- Bollinger Bands
- Real-time insights directly from a Snowflake-powered store

---


