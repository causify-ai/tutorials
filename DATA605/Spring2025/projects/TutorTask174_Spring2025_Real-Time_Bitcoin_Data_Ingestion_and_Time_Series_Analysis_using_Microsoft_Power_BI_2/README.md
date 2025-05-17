# Real-Time Bitcoin Data Ingestion and Time Series Analysis using Microsoft Power BI

**Author:** Abhishek Rithik Origanti  
**Date:** May 2025  
**Course:** DATA605 — Big Data Systems  
**Instructor:** Prof. Giovanni Saggesse

---

## 📌 Objective

This project demonstrates real-time ingestion, transformation, visualization, and forecasting of Bitcoin price data using a full-stack Python and Microsoft Power BI pipeline. It integrates data streaming and time series analysis techniques to produce a live dashboard with analytical insights.

---

## 📦 Project Components

### 🔁 1. API Data Ingestion
- Python script (`bitcoin_data_ingestion.py`) pulls real-time Bitcoin price and market cap data using the [CoinGecko API](https://www.coingecko.com/).
- Data is pushed to a `.csv` file (`bitcoin_price_transformed.csv`) or optionally streamed to Power BI using the REST API.

### 🧹 2. Data Preparation
- Cleaning, calculating moving averages, and computing percentage change.
- CSV data is updated every 60 seconds.

### 📊 3. Power BI Dashboard
- Live streaming dataset created via Power BI REST API.
- Dashboard shows:
  - Current Price (USD)
  - 7-Point Moving Average
  - Price Change (%)
  - Market Capitalization
  - Historical trends

### ⏱️ 4. Real-Time Analytics
- Uses **push dataset** to simulate real-time data updates in Power BI service.
- Streamed via `push_to_powerbi.py`.

### 📈 5. Time Series Analysis
Implemented in `bitcoin_example.ipynb` using:
- 7-minute Moving Average (Trend)
- **SARIMA model** to forecast next 60 minutes of price
- **Prophet model** for comparison
- **Seasonal decomposition** using `seasonal_decompose()` to detect trends, seasonality, and noise

---

## 📂 File Overview

| File | Description |
|------|-------------|
| `bitcoin_data_ingestion.py` | Script to fetch data from CoinGecko API |
| `bitcoin_price_transformed.csv` | Transformed data written by ingestion script |
| `push_to_powerbi.py` | Pushes real-time data to Power BI |
| `bitcoin_utils.py` | Helper functions for ingestion and transformation |
| `bitcoin_example.ipynb` | Notebook for trend, seasonality, and forecast analysis |
| `bitcoin_api.ipynb` | Describes API interaction with CoinGecko |
| `bitcoin_example.md` | Markdown documentation of time series and forecasting |
| `bitcoin_api.md` | Markdown documentation of the ingestion API |
| `Real-Time_Bitcoin_Dashboard.pbix` | Power BI dashboard file |
| `README.md` | This file |
| `docker_data605_style/` | Docker setup used for development |
| `bitcoin_example.html` | Exported version of the final notebook |
| `bitcoin_ingestion.log` | Logging output of the ingestion process |

---

## 🐳 Docker & Development

- Developed inside a thin-client Docker container using the `data605_style` setup.
- Source path:  
  `~/src/tutorials1/DATA605/Spring2025/projects/TutorTask174_Spring2025_Real-Time_Bitcoin_Data_Ingestion_and_Time_Series_Analysis_using_Microsoft_Power_BI_2/`

---

## 🚀 How to Run

1. **Run Data Ingestion (Locally or via Push API)**
   ```bash
   python bitcoin_data_ingestion.py

