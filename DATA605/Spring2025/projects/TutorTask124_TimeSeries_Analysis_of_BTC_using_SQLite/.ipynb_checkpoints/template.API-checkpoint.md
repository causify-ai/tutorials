# Bitcoin Daily Price Analysis with SQLite & CoinMarketCap API

A comprehensive notebook for fetching, storing, and analyzing Bitcoin (BTC) daily price and volume data using the CoinMarketCap API and SQLite. This notebook demonstrates best practices in data acquisition, storage, statistical analysis, and visualization for cryptocurrency market data.

---

## Table of Contents

- [Introduction](#introduction)
- [Notebook Structure](#notebook-structure)
- [Data Acquisition](#data-acquisition)
- [Database Operations](#database-operations)
- [Data Analysis](#data-analysis)
  - [Moving Averages](#moving-averages)
  - [Volume Analysis](#volume-analysis)
  - [Bollinger Bands](#bollinger-bands)
  - [Rate of Change](#rate-of-change)
  - [Volatility](#volatility)
  - [Distribution Analysis](#distribution-analysis)
- [Visualization](#visualization)
- [References](#references)
- [Citations](#citations)

---

## Introduction

This notebook provides a template for working with cryptocurrency data, specifically focusing on Bitcoin (BTC). It covers the process of fetching historical and live data, storing it in a local SQLite database, and performing a range of time series analyses and visualizations to understand BTC market trends.

---

## Notebook Structure

The workflow is designed to be clear and logical, following these main steps:

- Load data
- Compute statistics
- Clean data
- Recompute statistics if needed
- Perform analysis
- Visualize and present results

Each section is well-commented and follows reproducible data science practices.

---

## Data Acquisition

- Fetches historical BTC-USD daily data (covering up to 15 years).
- Retrieves live BTC pricing and market statistics from the CoinMarketCap API.
- Ensures data freshness by updating the database with the latest datapoints.

---

## Database Operations

- Stores all data in a local SQLite database (`btcDaily.db`).
- Supports querying for both historical and live BTC data.
- Example schema:

  | date                | close      | high       | low        | open       | volume        |
  |---------------------|------------|------------|------------|------------|---------------|
  | 2014-09-17-00-00-00 | 457.33     | 468.17     | 452.42     | 465.86     | 21056800      |
  | ...                 | ...        | ...        | ...        | ...        | ...           |

---

## Data Analysis

### Moving Averages

- Calculates 2-day, 30-day, and 120-day moving averages for opening price and volume using SQL window functions.
- Helps identify short-term and long-term market trends.

### Volume Analysis

- Analyzes BTC trading volume over time.
- Computes moving averages for volume to detect shifts in trading activity.

### Bollinger Bands

- Computes 20-day rolling mean and standard deviation for BTC opening price.
- Visualizes upper and lower Bollinger Bands to assess volatility and price extremes.

### Rate of Change

- Calculates percentage rate of change (1-day, 30-day, 120-day) for BTC opening price.
- Visualizes these changes to highlight momentum and trend reversals.

### Volatility

- Computes rolling standard deviation of daily returns over different windows (5, 30, 120 days).
- Visualizes volatility trends to understand market risk and stability.

### Distribution Analysis

- Plots the distribution (histogram) of daily returns.
- Highlights mean and median to provide statistical insight into BTC price behavior.

---

## Visualization

- **Line Plots:** BTC opening price and volume, with moving averages.
- **Candlestick Charts:** Price action with Bollinger Bands.
- **Bar Charts:** Percentage rate of change for different time windows.
- **Histograms:** Distribution of daily returns with mean and median markers.
- **Scatter Plots:** Highlights for current BTC price and volume.

---

## References

- [Jupyter Notebook Best Practices Guide](https://github.com/causify-ai/helpers/blob/master/docs/coding/all.jupyter_notebook.how_to_guide.md)
- [CoinMarketCap API Documentation](https://coinmarketcap.com/api/)
- [mplfinance Documentation](https://github.com/matplotlib/mplfinance)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [sqlite-utils Documentation](https://sqlite-utils.datasette.io/en/stable/)

---

## Citations

- Notebook structure and coding conventions are based on the causify-ai Jupyter notebook guide.
- Data sourced from the CoinMarketCap API and managed using `sqlite_utils`.

---

> This notebook is designed for clarity, reproducibility, and extensibility. For further customization or integration with other data sources, refer to the cited references and best practices guides.
