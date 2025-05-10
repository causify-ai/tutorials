# Bitcoin Price Forecasting with Facebook Prophet

Welcome to my capstone project for DATA605: an end-to-end Bitcoin forecasting system using Facebook Prophet, built with real-time data ingestion, EDA, time-series modeling, and optional Streamlit deployment.

---

## Table of Contents

1. [Project Objective](#project-objective)
2. [General Guidelines](#-general-guidelines)
3. [Architecture Overview](#-architecture-overview)
4. [Technologies & Libraries Used](#-technologies--libraries-used)
5. [Dataset Sources](#-dataset-sources)
6. [Utility Functions Explained](#-utility-functions-explained-utilspy)
7. [Exploratory Data Analysis (EDA)](#-exploratory-data-analysis-eda)
8. [Project Status](#-project-status)

---

## Project Objective

Forecasting cryptocurrency prices, particularly Bitcoin, is a challenging yet valuable task due to the asset’s high volatility and market sensitivity. Investors, analysts, and trading platforms rely on timely insights to make informed decisions. This project seeks to develop a reliable, real-time forecasting system that predicts short-term Bitcoin price movements using both historical and live data. Leveraging Facebook Prophet, a time series forecasting tool, the project is designed to process noisy and irregular financial data, model seasonality and trends, and produce accurate, interpretable forecasts. The system is also built to be robust against missing data, customizable for future improvements, and scalable for real-time applications.

-----

## General Guidelines

This section outlines general project practices followed to ensure a clean, reproducible implementation.

* **Docker + Jupyter Image**: The project is containerized with Docker. A Jupyter Lab image was used to execute all notebooks consistently across environments.
* **Clean Folder Structure**: Follows a modular layout (`data/`, `scripts/`, `notebooks/`, etc.).
* **Environment Management**: All dependencies are tracked in `requirements.txt` and used within a virtual environment.
* **Version Control**: Git is used with large data excluded via `.gitignore`.
* **Code Modularity**: Functions are separated into `utils.py` to keep notebooks clean.
* **Prophet Setup**:

  * Data uses `ds` and `y` columns.
  * Weekly seasonality disabled due to flat weekly trends.
  * Changepoint detection and log return analysis are used.
* **Deployment**: Streamlit used for an optional interactive forecast dashboard.

---

## Architecture Overview

1. **Data Ingestion**: Load historical CSV, fetch live API data
2. **Preprocessing**: Merge, clean, and validate continuity
3. **EDA**: Trend analysis, seasonality, volatility
4. **Modeling**: Prophet training
5. **Forecasting**: 7–30 day predictions
6. **Evaluation**: RMSE, MAE (planned)
7. **Deployment**:  Streamlit dashboard

---

## Technologies & Libraries Using in The Project

| Component     | Libraries/Tools             |
| ------------- | --------------------------- |
| Forecasting   | Facebook Prophet            |
| Data Handling | pandas, numpy               |
| API Ingestion | requests, json              |
| Visualization | matplotlib, seaborn, plotly |
| Evaluation    | sklearn.metrics             |
| Dashboard     | streamlit (optional)        |

---

## Dataset Sources

### Historical Data

* **Source**: [Kaggle BTC Historical Dataset](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data) (2012–2025)
* **Transformed**: `Date → ds`, `Close → y`

### Real-Time Data

* **Source**: CoinGecko API (`/coins/bitcoin/market_chart`)
* **Used**: Last 365 days’ prices for live forecasting

---

## Utility Functions Explained (`utils.py`)

### `load_historical_data(filepath)`

Reads historical Bitcoin data from a CSV file. Renames `Date` and `Close` to `ds` and `y`, respectively. Converts dates to datetime format for compatibility with Prophet.

### `fetch_live_data(days, currency)`

Uses the CoinGecko API to retrieve recent Bitcoin price data. Formats the data to match Prophet’s structure (`ds`, `y`) and handles time conversion from UNIX format.

### `merge_and_clean_data(historical_df, live_df)`

Combines the historical and live data into a single dataset. Ensures the data is continuous, removes duplicates, and sorts by date to prepare for modeling.

### `create_prophet_model()`

Instantiates a basic Facebook Prophet model. Can be extended with additional parameters such as holidays, custom seasonality, or tuned changepoint settings.

### `train_prophet_model(model, df)`

Fits the Prophet model using the cleaned dataset. Requires a DataFrame with `ds` and `y` columns. Outputs a trained model ready for forecasting.

### `make_forecast(model, periods)`

Generates a DataFrame with future dates and forecasts values for a given period. Includes predicted values, trend components, and confidence intervals.

### `plot_forecast(model, forecast)`

Visualizes the forecast using Prophet’s built-in plotting functions. Displays overall trend, seasonality components, and prediction intervals.

---

## Exploratory Data Analysis (EDA)

I conducted EDA to assess trend, volatility, and seasonal patterns in Bitcoin prices.

### Time Range & Continuity

* 2012–2025 daily data
* No missing or duplicate dates

### Trend & Summary Stats

* Mean: \~\$17,415, Median: \~\$6,610, Max: \~\$106,182
* Highly volatile with exponential growth patterns

### Distribution & Outliers

* Right-skewed distribution
* 100+ outliers detected via Z-score (>3)

### Seasonality

* **Weekly**: Negligible differences → excluded
* **Monthly**: Peaks Jan–Apr
* **Yearly**: Clear cyclic booms in 2013, 2017, 2021, 2024

### Changepoints

* Detected major structural breaks (>20% changes)
* Changepoints helped guide Prophet configuration

### Volatility Analysis

* 30-day rolling std showed clustered volatility
* Log returns used for stability

## Contextual Zoom-In Events

After carefully examining Bitcoin’s long-term price trend, seasonality charts, and volatility plots, I noticed repeated cycles of sharp surges, steep drops, and prolonged recovery phases. To better understand these shifts, I conducted further research into real-world financial events, regulatory decisions, and technological milestones that could explain these anomalies. Below is a breakdown of major turning points in the time series, each aligned with known historical events:

* **2013 Bull Run** — Bitcoin touches \$1,150
  *Month: December 2013*
  First major spike, driven by demand in Asia and increased media coverage.

* **2014 Mt. Gox Collapse** — Market-wide crash
  *Month: February 2014*
  The Mt. Gox exchange collapsed, triggering Bitcoin’s first bear market.

* **2017 ATH** — Bitcoin nears \$20,000
  *Month: December 2017*
  Fueled by the ICO boom and retail speculation.

* **2018 Crypto Winter** — Year-long decline
  *Month: December 2018*
  Driven by speculative excess correction and regulatory uncertainty.

* **COVID-19 Crash**
  *Month: March 2020*
  Global panic led to Bitcoin losing over 40% of its value in a single day.

* **2020 Halving** — Start of a new bull phase
  *Month: May 2020*
  Third halving reduced block rewards to 6.25 BTC, creating supply pressure.

* **2021 Bull Run — Twin Peaks**
  *Months: April and November 2021*
  Peaks driven by the Coinbase IPO and ETF anticipation.

* **FTX Collapse & Bear Market**
  *Month: November 2022*
  Major drop following the collapse of a top crypto exchange.

* **2024 Halving** — Bullish trend begins again
  *Month: April 2024*
  Fourth halving reduced block rewards to 3.125 BTC, historically marking new growth phases.

After identifying these key inflection points through trend and volatility analysis, I conducted additional research into macroeconomic and market-specific events to better contextualize the anomalies. While modeling is yet to be implemented, this understanding offers valuable insights into how changepoint detection and seasonality components can be configured in Facebook Prophet. The relationship between observed historical spikes and external events provides a strong foundation for developing interpretable and realistic forecasting models in the next phase of the project.

**Reference**: [Bitcoin Price History: Timeline of Its Evolution (2009–2025) – Kraken](https://www.kraken.com/learn/bitcoin-price-history)

---

## Project Status

| Phase         | Status | Notes                         |
| ------------- | ------ | ----------------------------- |
| Ingestion     | Done   | Historical + live merged      |
| EDA           | Done   | Seasonality, outliers, trends |
| Modeling      | To Do  | Prophet trained               |
| Forecasting   | To Do  | Forecast generated            |
| Evaluation    | To Do  | Metrics computation upcoming  |
| Streamlit App | To Do  | Web app development           |
