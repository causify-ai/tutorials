# Collaborative Bitcoin Market Analysis & Forecasting with Hex

**Author:** Juhi Ramod  
**Course:** DATA605 – Big Data Systems, Spring 2025  
**Instructor:** Giacinto Paolo  Saggese  
**Institution:** University of Maryland

---

## 📘 Project Description

This project explores time-series analysis and forecasting techniques to model and visualize the behavior of Bitcoin in relation to macroeconomic and social indicators. Using Hex as an interactive data workspace, the system ingests real-time data from CoinGecko and Alpha Vantage APIs, processes the data in a Dockerized Jupyter environment, and presents dynamic forecasting and anomaly detection using Prophet.

---

## 🧭 Objective

- Analyze Bitcoin price behavior using rolling metrics (volatility, correlation)
- Correlate Bitcoin with gold prices using 30-day rolling window
- Detect anomalies (>5% daily drops) in BTC pricing
- Forecast future Bitcoin prices using the Prophet model
- Present results via a collaborative, interactive Hex dashboard

---

## 🧰 Technologies Used

- **Hex.tech** – For interactive notebooks and dashboards  
- **Python** – Core logic and data analysis  
- **Prophet** – Time-series forecasting  
- **Plotly** – Visualizations  
- **CoinGecko API** – Real-time Bitcoin price data  
- **Alpha Vantage API** – Macroeconomic data (gold prices)  
- **Docker** – Containerized development environment  
- **Git** – Version control  

---

## 🔁 Project Pipeline

1. **Data Ingestion:**
   - Pull Bitcoin prices using CoinGecko API
   - Pull gold prices using Alpha Vantage
2. **Preprocessing:**
   - Standardize timestamps, format datasets
   - Merge Bitcoin and gold datasets on date
3. **Analysis:**
   - Calculate 30-day rolling volatility for Bitcoin
   - Compute 30-day rolling correlation with gold
   - Detect 5%+ BTC price drops
4. **Forecasting:**
   - Train Prophet model on historical BTC data
   - Predict prices for a 30–90 day horizon
5. **Presentation:**
   - Visualize results with Plotly
   - Embed insights in Hex dashboard

---

Sample Outputs
BTC Price vs. 30-Day Volatility Chart

BTC vs. Gold Rolling Correlation

Table of BTC 5% Drop Anomalies

Prophet Forecast (Next 30–90 Days)


---

## 🌐 Hex Dashboard Link

View the full analysis and forecasting in the published Hex app:  
👉 https://app.hex.tech/2d7ad7bc-cfca-4cd7-a6ae-9fb1aa7537f1/app/019621eb-178e-7005-8438-6b65b7cf6e35/latest




