# Bitcoin Price Forecasting with Facebook Prophet

Welcome to my capstone project for DATA605: an end-to-end Bitcoin forecasting system using Facebook Prophet, built with real-time data ingestion, EDA, time-series modeling, and  Streamlit deployment.

----

## Table of Contents

1. [Project Objective](#project-objective)
2. [General Guidelines](#general-guidelines)
3. [Architecture Overview](#architecture-overview)
4. [Technologies & Libraries Used](#technologies--libraries-used)
5. [Dataset Sources](#dataset-sources)
6. [Utility Functions Explained (utils.py)](#utility-functions-explained-utilspy)
7. [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
8. [Modeling](#modeling)
9. [Forecasting](#forecasting)
10. [Evaluation](#evaluation)
11. [Streamlit Dashboard](#streamlit-dashboard)
12. [Project Status](#project-status)

---

## Project Objective

Forecasting cryptocurrency prices, particularly Bitcoin, is a challenging yet valuable task due to the asset’s high volatility and market sensitivity. Investors, analysts, and trading platforms rely on timely insights to make informed decisions. This project seeks to develop a reliable, real-time forecasting system that predicts short-term Bitcoin price movements using both historical and live data. Leveraging Facebook Prophet, a time series forecasting tool, the project is designed to process noisy and irregular financial data, model seasonality and trends, and produce accurate, interpretable forecasts. The system is also built to be robust against missing data, customizable for future improvements, and scalable for real-time applications.

-----

## General Guidelines

This section outlines general project practices followed to ensure a clean, reproducible implementation.

* *Docker + Jupyter Image*: The project is containerized with Docker. A Jupyter Lab image was used to execute all notebooks consistently across environments.
* *Clean Folder Structure*: Follows a modular layout (data/, scripts/, notebooks/, etc.).
* *Environment Management*: All dependencies are tracked in requirements.txt and used within a virtual environment.
* *Version Control*: Git is used with large data excluded via .gitignore.
* *Code Modularity*: Functions are separated into utils.py to keep notebooks clean.
* *Prophet Setup*:

  * Data uses ds and y columns.
  * Weekly seasonality disabled due to flat weekly trends.
  * Changepoint detection and log return analysis are used.
* *Deployment*: Streamlit used for an interactive forecast dashboard.

---

## Architecture Overview

1. *Data Ingestion*: Load historical CSV, fetch live API data
2. *Preprocessing*: Merge, clean, and validate continuity
3. *EDA*: Trend analysis, seasonality, volatility
4. *Modeling*: Prophet training
5. *Forecasting*: 7–30 day predictions
6. *Evaluation*: RMSE, MAE (planned)
7. *Deployment*:  Streamlit dashboard

---

## Technologies & Libraries Using in The Project

| Component     | Libraries/Tools             |
| ------------- | --------------------------- |
| Forecasting   | Facebook Prophet            |
| Data Handling | pandas, numpy               |
| API Ingestion | requests, json              |
| Visualization | matplotlib, seaborn, plotly |
| Evaluation    | sklearn.metrics             |
| Dashboard     | streamlit                   |

---

## Dataset Sources

### Historical Data

* *Source*: [Kaggle BTC Historical Dataset](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data) (2012–2025)
* *Transformed*: Date → ds, Close → y

### Real-Time Data

* *Source*: CoinGecko API (/coins/bitcoin/market_chart)
* *Used*: Last 365 days’ prices for live forecasting

---

## Utility Functions Explained (utils.py)

### load_historical_data(filepath)

Reads historical Bitcoin data from a CSV file. Renames Date and Close to ds and y, respectively. Converts dates to datetime format for compatibility with Prophet.

### fetch_live_data(days, currency)

Uses the CoinGecko API to retrieve recent Bitcoin price data. Formats the data to match Prophet’s structure (ds, y) and handles time conversion from UNIX format.

### merge_and_clean_data(historical_df, live_df)

Combines the historical and live data into a single dataset. Ensures the data is continuous, removes duplicates, and sorts by date to prepare for modeling.

### create_prophet_model()

Instantiates a basic Facebook Prophet model. Can be extended with additional parameters such as holidays, custom seasonality, or tuned changepoint settings.

### train_prophet_model(model, df)

Fits the Prophet model using the cleaned dataset. Requires a DataFrame with ds and y columns. Outputs a trained model ready for forecasting.

### make_forecast(model, periods)

Generates a DataFrame with future dates and forecasts values for a given period. Includes predicted values, trend components, and confidence intervals.

### plot_forecast(model, forecast)

Visualizes the forecast using Prophet’s built-in plotting functions. Displays overall trend, seasonality components, and prediction intervals.

---

## Exploratory Data Analysis (EDA)

I conducted EDA to assess trend, volatility, and seasonal patterns in Bitcoin prices.

### Time Range & Continuity

* 2012–2025 daily data
* No missing or duplicate dates

### Trend & Summary Stats

* Mean: \\$17,415, Median: \\$6,610, Max: \~\$106,182
* Highly volatile with exponential growth patterns

### Distribution & Outliers

* Right-skewed distribution
* 100+ outliers detected via Z-score (>3)

### Seasonality

* *Weekly*: Negligible differences → excluded
* *Monthly*: Peaks Jan–Apr
* *Yearly*: Clear cyclic booms in 2013, 2017, 2021, 2024

### Changepoints

* Detected major structural breaks (>20% changes)
* Changepoints helped guide Prophet configuration

### Volatility Analysis

* 30-day rolling std showed clustered volatility
* Log returns used for stability

## Contextual Zoom-In Events

After carefully examining Bitcoin’s long-term price trend, seasonality charts, and volatility plots, I noticed repeated cycles of sharp surges, steep drops, and prolonged recovery phases. To better understand these shifts, I conducted further research into real-world financial events, regulatory decisions, and technological milestones that could explain these anomalies. Below is a breakdown of major turning points in the time series, each aligned with known historical events:

* *2013 Bull Run* — Bitcoin touches \$1,150
  Month: December 2013
  First major spike, driven by demand in Asia and increased media coverage.

* *2014 Mt. Gox Collapse* — Market-wide crash
  Month: February 2014
  The Mt. Gox exchange collapsed, triggering Bitcoin’s first bear market.

* *2017 ATH* — Bitcoin nears \$20,000
  Month: December 2017
  Fueled by the ICO boom and retail speculation.

* *2018 Crypto Winter* — Year-long decline
  Month: December 2018
  Driven by speculative excess correction and regulatory uncertainty.

* *COVID-19 Crash*
  Month: March 2020
  Global panic led to Bitcoin losing over 40% of its value in a single day.

* *2020 Halving* — Start of a new bull phase
  Month: May 2020
  Third halving reduced block rewards to 6.25 BTC, creating supply pressure.

* *2021 Bull Run — Twin Peaks*
  Months: April and November 2021
  Peaks driven by the Coinbase IPO and ETF anticipation.

* *FTX Collapse & Bear Market*
  Month: November 2022
  Major drop following the collapse of a top crypto exchange.

* *2024 Halving* — Bullish trend begins again
  Month: April 2024
  Fourth halving reduced block rewards to 3.125 BTC, historically marking new growth phases.

After identifying these key inflection points through trend and volatility analysis, I conducted additional research into macroeconomic and market-specific events to better contextualize the anomalies. While modeling is yet to be implemented, this understanding offers valuable insights into how changepoint detection and seasonality components can be configured in Facebook Prophet. The relationship between observed historical spikes and external events provides a strong foundation for developing interpretable and realistic forecasting models in the next phase of the project.

*Reference*: [Bitcoin Price History: Timeline of Its Evolution (2009–2025) – Kraken](https://www.kraken.com/learn/bitcoin-price-history)

---

Here’s the fully detailed and explanatory version of the *Modeling, **Forecasting, and **Evaluation* sections:

---

## Modeling

###  *Data Preparation & Feature Engineering (In-Depth)*

The modeling process begins with meticulous data preparation to ensure the time series data is clean, continuous, and properly structured for analysis.

- Dataset Range: Spanning from 2012 to 2025, this project combines long-term historical data with real-time data, capturing multiple Bitcoin market cycles, including bull runs, crashes, and recoveries.
- *Target Variable*: Bitcoin's closing price (y), which represents the daily final price and serves as the prediction target.
- *Datetime Handling*: The Prophet library requires a ds column representing dates. All datetime columns were standardized to meet this requirement.

*Feature Engineering through External Regressors*
To improve the model’s awareness of real-world events affecting price trends, several binary and numerical regressors were added:

| Regressor Name        | Purpose                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| doubling_flag       | Indicates historical price-doubling events that often precede increased volatility.               |
| volatility_flag     | Marks high volatility periods to help the model adjust predictions during unstable markets.       |
| etf_approval_flag   | Captures the effect of regulatory events such as ETF approvals, which historically impact prices. |
| exchange_crash_flag | Flags events like the FTX collapse to account for market-wide crashes.                            |
| rolling_volatility  | 30-day rolling mean of closing prices to provide short-term trend awareness.                      |

*Holidays Incorporated*
Bitcoin halving events were explicitly included as custom holidays, as these events historically trigger significant price shifts.

* Dates: 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20

---

###  *Prophet Model Configuration*

The Prophet model was carefully tuned to capture the non-linear and highly volatile nature of Bitcoin price movements.

- Growth Type: Set to **Linear*, as this allows the model to track general growth trends while relying on changepoints to capture sudden shifts.

* *Seasonality*:

  * *Yearly Seasonality*: Enabled to model yearly cycles observed in the crypto market.
  * *Weekly Seasonality*: Disabled after EDA confirmed weekly trends had minimal influence.
  * *Monthly Seasonality*: Manually added with a Fourier order of 5 to capture known monthly trends, especially price increases between January and April.
  * *Seasonality Mode: Set to **Multiplicative* to handle the exponential growth patterns seen in Bitcoin.

* *Changepoint Detection*:

  * n_changepoints = 100 ensured that the model could capture sharp market movements, such as those during the COVID-19 crash and the FTX collapse.
  * changepoint_prior_scale = 1.0 provided a balance between model flexibility and overfitting prevention.

---

###  *Model Training Results*

| Metric | Training Set |
| ------ | ------------ |
| RMSE   | 1,736.53 USD |
| MAE    | 929.40 USD   |
| MAPE   | 43.58%       |

*Analysis of Training Performance*

* The model successfully captured historical Bitcoin trends, including both extended bull markets (2013, 2017, 2021) and harsh bear markets (2014, 2018, 2022).
* Although sharp, extreme spikes in price were slightly underpredicted (a common limitation in financial modeling), the overall trend and cyclic behavior were accurately reflected.
* Incorporating external regressors and holidays greatly improved the model’s interpretability, enabling more realistic and explainable predictions.

---

##  Forecasting

###  *Forecasting Configuration*

* *Forecast Horizon*: 365 days, providing one full year of future price predictions.
* *Test Period*: 2023 – 2025 was chosen to validate the model against recent volatile periods, including the 2024 halving event and post-pandemic economic fluctuations.

The Prophet model was used to generate forecasts along with upper and lower bounds, which quantify the uncertainty inherent in Bitcoin price predictions.

---

### *Forecasting Insights*

* The model successfully captured the broad direction of the market across both upward rallies and sharp corrections.
* Confidence intervals effectively highlighted uncertain periods, especially around historically volatile events such as regulatory announcements and macroeconomic turbulence.
* Despite the complexity and unpredictability of cryptocurrency markets, the model demonstrated its ability to forecast within an acceptable margin of error.

---

#  Evaluation

### *Evaluation Metrics (On Test Set)*

| Metric | Value         |
| ------ | ------------- |
| RMSE   | 13,424.78 USD |
| MAE    | 9,817.14 USD  |
| MAPE   | 16.96%        |

*In-Depth Evaluation Analysis*

* *RMSE (Root Mean Square Error)*: Measures the average magnitude of prediction errors. While high due to the large absolute values of Bitcoin, it is within an acceptable range for financial assets.
* *MAE (Mean Absolute Error)*: Provides a direct interpretation of the average prediction error in USD terms, demonstrating reasonably accurate predictions.
* *MAPE (Mean Absolute Percentage Error): A MAPE of **16.96%* is highly competitive for financial time series data and indicates that the model's forecasts were quite reliable even during volatile periods.

*Key Takeaways*

* Prediction accuracy was robust despite high market volatility in the test period.
* External regressors played a significant role in reducing prediction errors by allowing the model to adjust dynamically during impactful events.
* The model was most challenged during periods of unprecedented price surges, a limitation common to most time series forecasting models.

----

## Streamlit Dashboard

An interactive Streamlit dashboard was developed to visualize Bitcoin price forecasts and historical trends. The dashboard enhances user experience by offering real-time exploration, customizable filters, and professional-quality visualizations.

*Live Dashboard Link*: [Bitcoin Forecast Dashboard](https://btc-forecasting-using-facebook-prophet.streamlit.app/)

---

### *Key Features*

* *User-Friendly Interface*:

  * Modern, clean design with customized CSS styling.
  * Clear headings, organized layout, and intuitive navigation.

* *Interactive Forecast Controls*:

  * Filter forecasts by *Year, **Month, or a specific **Date*.
  * Instantly view Bitcoin price predictions for selected periods.

* *Forecast Visualization*:

  * Short-term (Next 30 days) and long-term (1 year ahead) forecasts.
  * Visualizations include historical price trends, forecast overlays, and Prophet model components (trend, seasonality, and holiday effects).

* *Downloadable Data*:

  * Users can download the next 30-day forecast as a CSV file for further analysis.

* *Performance Metrics*:

  * Real-time display of key evaluation metrics: *RMSE, **MAE, and **MAPE* to assess model accuracy.

* *Historical Events & Articles*:

  * Highlights of major Bitcoin market events like the 2013 Bull Run, 2017 ICO Boom, 2022 FTX Collapse, and the 2024 Halving, providing context to market movements.

---


## Project Status

| Phase         | Status | Notes                         |
| ------------- | ------ | ----------------------------- |
| Ingestion     | Done   | Historical + live merged      |
| EDA           | Done   | Seasonality, outliers, trends |
| Modeling      | Done   | Prophet trained               |
| Forecasting   | Done   | Forecast generated            |
| Evaluation    | Done   | Metrics computation upcoming  |
| Streamlit App |Deployed| Web app for dashboards         |
