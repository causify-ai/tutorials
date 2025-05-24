# Example Application: Collaborative Bitcoin Market Analysis & Forecasting

## 📐 Architecture Overview

This application demonstrates a full pipeline for real-time Bitcoin price analysis and forecasting using public APIs, a reusable Python logic layer, and Jupyter notebooks for interactive visualization. It replicates many of the functions of a production-grade data analytics system but within an academic setting and Dockerized development environment.

---

## 🔄 Pipeline Flow

1. **Fetch live Bitcoin prices** using the CoinGecko API
2. **Fetch daily gold prices** using Alpha Vantage API
3. **Clean and merge** both datasets using `pandas`
4. **Compute analytics**, including:
   - 30-day rolling volatility
   - 30-day rolling correlation with gold
   - Daily percent change for anomaly detection
5. **Forecast BTC price** using Prophet
6. **Visualize results** using Plotly
7. (Optional) **Publish insights in Hex** as a live dashboard

---

## 🛠️ Data Sources

### 1. CoinGecko API
The function `get_btc_price()` in `btc_utils.py` connects to:
It retrieves the current USD price of 1 Bitcoin.

### 2. Alpha Vantage API
The function `get_gold_price()` retrieves the latest time-series data for gold prices via the `TIME_SERIES_DAILY` endpoint. The output is transformed to match Bitcoin data formatting.

---

## 🧱 Utility Layer (btc_utils.py)

Reusable Python functions abstract away API logic and simplify analysis steps.  
Key functions include:

- `get_btc_price()` – Pulls current Bitcoin price  
- `get_btc_history()` – Pulls historical BTC prices for trend analysis  
- `get_gold_price()` – Retrieves historical gold prices  
- `calculate_volatility()` – Computes 30-day rolling volatility  
- `calculate_correlation()` – Computes BTC-gold correlation  
- `detect_anomalies()` – Flags >5% BTC price drops  
- `forecast_btc_prices()` – Fits Prophet and returns predictions  

---

## 🔄 Forecasting Loop

The forecasting loop supports dynamic adjustment of the forecast horizon (e.g., 30, 60, or 90 days).  
A Jupyter notebook (`btc.example.ipynb`) demonstrates:

- Loading cleaned data
- Calling `forecast_btc_prices()` from the utility module
- Plotting forecasts using Prophet’s `plot_plotly()`

This setup simulates production-ready analytics that can be extended to dashboards or reports.

---

## 📊 Time Series Analysis & Visualization

The visualizations include:

- BTC price over time  
- 30-day moving average and rolling standard deviation  
- BTC vs. Gold correlation plot  
- Anomaly table (for >5% drops)  
- Forecast chart with upper/lower bounds

All visualizations use `plotly` for interactivity and clarity.

---

## ✅ Outcome

This project bridges:

- Real-world crypto data ingestion  
- A reusable Python logic layer for transformation and analysis  
- Clean, interactive notebooks for sharing and reproducibility  
- Optional Hex dashboard for external access

The system is modular and can be scaled for additional assets, longer timeframes, or richer forecasting models.

