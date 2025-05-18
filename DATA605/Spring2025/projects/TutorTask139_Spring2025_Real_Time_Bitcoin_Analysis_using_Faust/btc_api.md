# 📈 `btc_api.ipynb` – Real-Time BTC Visualization & Forecasting Dashboard

This Jupyter Notebook acts as a live analytics dashboard for monitoring Bitcoin prices in real-time. It collects, processes, visualizes, and forecasts Bitcoin price data using API calls, live plotting, and ARIMA time series modeling.

---

## What This Notebook Does:
- Fetches BTC data every 60 seconds (price, 24h volume, % change)
- Plots real-time **line charts** for price and **bar charts** for volume
- Calculates rolling statistics (moving averages & volatility)
- Raises alerts for sudden price changes
- Uses an **ARIMA model** to forecast the next 3 price values
- Auto-updates every minute for a continuous live dashboard experience

---

## Cell Breakdown

### 🔹 Cell 1 – Import Libraries & Set Styling
Imports all necessary tools:
- `requests`, `pandas`, `matplotlib` for data fetching and plotting
- `datetime`, `time`, `statistics` for processing
- `ARIMA` from `statsmodels` for forecasting
- Sets a clean `seaborn-darkgrid` visual theme with custom figure aesthetics

---

### 🔹 Cell 2 – Define API Function and Buffers
- Initializes empty Python lists (buffers) for time, price, volume, and % change
- Defines a function `retrieve_btc_snapshot()` that connects to the **CoinGecko API**
- Returns structured BTC data in a dictionary format

---

### 🔹 Cells – Real-Time Loop, Plotting, and ARIMA Forecasting
- Starts a `while True:` loop that fetches and appends new BTC data every 60s
- Calculates:
  - 5/15/30-point moving averages
  - Price volatility (standard deviation)
  - % change between last two points
- Generates live plots with:
  - BTC price (with rolling average lines)
  - 24h volume as bars
- Prints analysis and ARIMA-based price forecasts if enough data points are collected
- Displays alerts when % change > ±2%

---

## 💡 Console Output

```
Analysis (2025-05-17 18:08:29)
Current Price: $103,225.00
5-point MA: $103,231.60
15-point MA: $103,243.07
30-point MA: $103,251.90
Volatility: 14.97
[ARIMA Forecast] Next 3 BTC Prices: $103,267.00, $103,280.22, $103,292.45
```

---

## 📚 What You'll Learn
- How to build a live analytics dashboard in Jupyter
- Use of public APIs for real-time financial data
- Applying statistical methods like moving averages and volatility
- How to use and interpret **ARIMA forecasts** in a real-time context

---

## ⚙️ Dependencies
```
matplotlib
pandas
requests
statsmodels
datetime
time
```

---

## 🎉 Summary
This notebook complements the Kafka-Faust stream setup by providing a **visual interface** and **forecasting engine** for real-time Bitcoin price data. Ideal for financial analysis, trading simulations, or real-time system demonstrations.

