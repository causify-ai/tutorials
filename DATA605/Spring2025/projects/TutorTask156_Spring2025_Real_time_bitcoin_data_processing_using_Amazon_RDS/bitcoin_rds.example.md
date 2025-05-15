<!-- toc -->

- [Real-time Bitcoin Data Analysis using Amazon RDS](#real-time-bitcoin-data-analysis-using-amazon-rds)
  * [Introduction](#introduction)
  * [System Architecture](#system-architecture)
  * [Implementation](#implementation)
    + [Database Setup](#database-setup)
    + [Data Collection](#data-collection)
    + [Time Series Analysis](#time-series-analysis)
    + [Visualization and Insights](#visualization-and-insights)
  * [Key Findings](#key-findings)
  * [Conclusion](#conclusion)

<!-- tocstop -->

# Real-time Bitcoin Data Analysis using Amazon RDS

## Introduction

This project demonstrates a complete workflow for collecting, storing, and analyzing Bitcoin price data using Amazon RDS PostgreSQL and the CoinGecko API. The system provides near real-time monitoring of Bitcoin price movements and supports various time series analyses for market insights.

The project showcases how to:
- Set up and manage a PostgreSQL database on Amazon RDS
- Collect and store Bitcoin price data from public APIs
- Implement time series analysis on financial data
- Create informative visualizations of market trends
- Analyze key indicators like price movement, volume, RSI, and volatility

## System Architecture

The implementation consists of three main components working together:

1. **Data Source**: CoinGecko's cryptocurrency API provides both real-time and historical Bitcoin market data.
2. **Data Storage**: Amazon RDS PostgreSQL database serves as a persistent storage solution for the price data.
3. **Analysis Layer**: Python code processes the data and implements various time series analyses.

The workflow follows these steps:
1. Connect to the Amazon RDS PostgreSQL database
2. Create necessary database tables if they don't exist
3. Fetch historical Bitcoin data from CoinGecko API
4. Store the data in the PostgreSQL database
5. Retrieve the stored data for analysis
6. Perform time series analyses and visualizations
7. Collect and store current Bitcoin data in real-time

## Implementation

### Database Setup

The project begins by establishing a connection to an Amazon RDS PostgreSQL database and ensuring that the necessary tables exist:

```python
# Database connection
conn = brds.get_db_connection()

# Create necessary tables
brds.create_tables_if_not_exist()
```

Two main tables are used in this implementation:
- `raw_bitcoin_prices`: Stores raw price data points with timestamp
- `hourly_bitcoin_prices`: Stores OHLC (Open, High, Low, Close) aggregated hourly data

### Data Collection

Historical Bitcoin data is collected from the CoinGecko API and stored in the database:

```python
# Fetch and store 60 days of historical Bitcoin data
records_inserted = brds.fetch_and_store_historical_bitcoin_data(days=60)
```

The data includes:
- Price in USD
- Trading volume
- Market capitalization
- Timestamp for each data point

### Time Series Analysis

The project implements several time series analyses to understand Bitcoin price movements:

1. **Basic Price Trend Visualization**: Plotting price over time to visualize the overall direction
2. **Moving Average Analysis**: Calculating and visualizing both short-term (24-hour) and long-term (7-day) moving averages to identify trends
3. **Volume Analysis**: Examining trading volume patterns and their relationship to price changes
4. **Daily Returns Analysis**: Calculating daily price changes to understand volatility
5. **RSI (Relative Strength Index)**: Identifying potential overbought or oversold conditions in the market

These analyses provide a comprehensive view of Bitcoin market behavior from multiple angles.

### Visualization and Insights

The project creates various visualizations to make the data interpretable:

```python
# Plot Bitcoin price with moving averages
plt.figure(figsize=(12, 6))
plt.plot(df_with_ma['timestamp'], df_with_ma['price_usd'], 'b-', 
         label='Bitcoin Price', alpha=0.6)
plt.plot(df_with_ma['timestamp'], df_with_ma['MA_24h'], 'r-', 
         label='24-hour Moving Average', linewidth=2)
plt.plot(df_with_ma['timestamp'], df_with_ma['MA_7d'], 'g-', 
         label='7-day Moving Average', linewidth=2)
```

The visualizations include:
- Price trend charts
- Volume bar charts
- Combination charts showing price and volume together
- Daily returns visualizations
- Technical indicators like RSI

Special events that impact the market are highlighted with vertical lines, specifically:
- April 9, 2025: Trump's tariff increase to 125% on Chinese goods
- May 12, 2025: U.S.-China temporary trade deal in Geneva

## Key Findings

The analysis provides several key insights about Bitcoin's market behavior:

1. **Price Trend**: The overall direction of Bitcoin prices over the analyzed period, including percentage change
2. **Market Volatility**: Metrics on average daily change and price stability
3. **Trading Volume Patterns**: Analysis of trading activity and its relationship to price
4. **Technical Indicators**: Moving averages and RSI readings that signal potential market momentum

The project demonstrates how data analysis can reveal patterns that might not be obvious from simply observing price charts.

## Conclusion

This project showcases a complete data pipeline for cryptocurrency market analysis using Amazon RDS and the CoinGecko API. The implementation demonstrates:

1. How to set up a cloud database for financial data storage
2. Techniques for retrieving and storing time series data
3. Methods for analyzing cryptocurrency market movements
4. Approaches for visualizing financial data effectively

The modular design using utility functions makes the system extensible for additional analyses or cryptocurrencies. This approach provides a foundation for more sophisticated financial analytics applications, including predictive modeling or automated trading strategies.
