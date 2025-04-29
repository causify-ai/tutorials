
# Streamlit.API.md

## Overview

This markdown file documents the structure, purpose, and functionality of the `XYZ.API_final_with_metadata.ipynb` notebook. The notebook serves as a demonstration of how to use a native CoinGecko API in conjunction with a Python-based wrapper module `XYZ_utils` to perform common cryptocurrency analytics tasks.

---

## Objectives

The main objectives of the notebook are:

- **Fetch real-time price data** for a specific cryptocurrency (e.g., Bitcoin)
- **Retrieve historical data** for technical analysis
- **Calculate moving averages** to identify price trends
- **Compute technical indicators** (e.g., RSI, MACD)
- **Detect anomalies** in price data that could indicate unusual market behavior
- **Promote modular and reusable code** via the `XYZ_utils` wrapper layer

---

## Structure & Flow

The notebook follows a logical flow designed for both demonstration and educational purposes:

1. **Introduction**  
   Brief overview of the CoinGecko API and its relevance in crypto analytics.

2. **Notebook Setup and Imports**  
   Imports necessary functions from `XYZ_utils`.

3. **Fetch Current Price**  
   Uses the wrapper function `get_current_price()` to obtain the latest price of Bitcoin.

4. **Fetch Historical Data**  
   Retrieves the last 30 days of Bitcoin price data using `get_historical_data()`.

5. **Moving Average Calculation**  
   Applies a 7-day moving average to the historical dataset using `calculate_moving_average()`.

6. **Technical Indicator Computation**  
   Leverages `calculate_technical_indicators()` to compute popular financial indicators.

7. **Anomaly Detection**  
   Invokes `detect_anomalies()` to flag data points that significantly deviate from trends.

---

## API Layer and Wrapper

The `XYZ_utils.py` file acts as an abstraction layer over the raw CoinGecko API. It includes the following core methods:

- `get_current_price(coin_id: str) -> float`
- `get_historical_data(coin_id: str, days: int) -> pd.DataFrame`
- `calculate_moving_average(df: pd.DataFrame, window: int) -> pd.DataFrame`
- `calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame`
- `detect_anomalies(df: pd.DataFrame) -> pd.DataFrame`

These functions encapsulate request handling, JSON parsing, error checking, and data transformation steps, making the notebook cleaner and easier to maintain.

---

## Key Dependencies

- `requests` – for API communication
- `pandas` – for data handling and manipulation
- `ta` – for technical indicator calculations
- `matplotlib`/`plotly` – for visualization (optional)

---

## References

- CoinGecko API documentation: https://www.coingecko.com/en/api/documentation  
- Python for Data Analysis – Wes McKinney  
- Investopedia articles on [Moving Averages](https://www.investopedia.com/terms/m/movingaverage.asp) and [Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)

---

## Citations

- CoinGecko. (2024). *CoinGecko API v3*. Retrieved from https://www.coingecko.com/en/api/documentation  
- McKinney, W. (2018). *Python for Data Analysis*. O’Reilly Media.

---

## Future Improvements

- Include support for additional coins beyond Bitcoin
- Add interactive visualizations
- Implement alerting system for detected anomalies

---


---

## Additional Features to Explore in CoinGecko API

Beyond price and historical data, the CoinGecko API provides access to a wide variety of cryptocurrency metrics and insights:

### 1. **Market Data**
- `/coins/markets` – Get current data (name, price, market, ...).
- `/coins/{id}/market_chart` – Get historical market data (prices, market caps, total volumes).

### 2. **Global Market Data**
- `/global` – Fetch global cryptocurrency market data including total market cap, total volume, active markets, and Bitcoin dominance.

### 3. **Coin Information**
- `/coins/{id}` – Detailed coin information including whitepaper links, categories, development status, and more.
- `/coins/{id}/tickers` – Get exchange tickers (price, volume, exchange name).

### 4. **Trending Coins**
- `/search/trending` – Discover which coins are currently trending on CoinGecko.

### 5. **Derivatives and Exchanges**
- `/derivatives` – Data about derivative markets.
- `/exchanges` – Exchange-level data such as volume, trust score, and listed coins.

### 6. **NFTs**
- `/nfts/list` and `/nfts/{id}` – Fetch NFT project metadata and market metrics.

### 7. **Developer and Community Metrics**
- `/coins/{id}` – Includes GitHub statistics, Reddit subscribers, Telegram users, etc.

---

These features can be used to:
- Build watchlists or dashboards
- Analyze token performance across exchanges
- Investigate market sentiment and developer activity
- Research NFT trends and project details

Refer to the [official documentation](https://www.coingecko.com/en/api/documentation) for full details on endpoints and parameters.
