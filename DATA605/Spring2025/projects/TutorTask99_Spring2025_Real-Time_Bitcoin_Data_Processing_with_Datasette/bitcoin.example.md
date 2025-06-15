# Bitcoin.example.md

## Overview

This notebook demonstrates the full pipeline for real-time Bitcoin data processing using Datasette technologies. It showcases how to:

- Fetch historical and real-time pricing data from CoinGecko
- Store structured data into an SQLite database
- Perform meaningful time series analysis including anomaly detection and trend decomposition
- Visualize results to gain insight into market behavior

---

## Key Steps Demonstrated

1. **Data Ingestion**
   - Historical data (last 365 days)
   - Real-time price snapshot
   - Both stored in `bitcoin_data.db` via utility functions

2. **Data Loading**
   - Pull complete dataset from SQLite using SQL queries

3. **Time Series Analysis**
   - Moving Averages: 7, 30, 90-day windows
   - Rolling Volatility: based on standard deviation
   - Z-score Anomaly Detection: flag unusual price changes
   - Cumulative Returns: compound investment growth view
   - STL Decomposition: splits the price signal into trend, seasonal, and residual components

---

## Visualizations

- Line plots of price trends
- Multi-window moving average overlays
- Highlighted anomalies on time series
- Rolling volatility curves
- Cumulative return growth
- STL trend-seasonality decomposition

These plots are designed to help users interpret market shifts, trading windows, and sudden price events.

---

## Takeaways

- Bitcoin price is volatile but shows seasonal and trend structures over time
- Anomaly detection helps identify sudden market moves (e.g., news-driven spikes)
- Rolling metrics like volatility and moving average are crucial for trading models

---

## Next Steps

This example can be extended by:
- Scheduling ingestion jobs for live updates
- Integrating Datasette to publish and explore the SQLite database via web
- Adding support for multi-coin comparisons or external indicators (e.g., stock indices)

This notebook serves as a foundational tutorial to work with time series financial data and build robust pipelines with Datasette and SQLite.
