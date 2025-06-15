<!-- toc -->

- [Project Title](#project-title)
  * [Table of Contents](#table-of-contents)
  * [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
- [Project Description](#project-description)
- [Technology Stack](#technology-stack)
- [Architecture & Workflow](#architecture--workflow)
- [API/Data Source](#apidatasource)
- [Data Cleaning](#data-cleaning)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Time Series Modeling](#time-series-modeling)
- [Visualization and Interpretation](#visualization-and-interpretation)
- [Key Insights and Results](#key-insights-and-results)
- [Conclusion](#conclusion)

<!-- tocstop -->

# Project Title

Real-Time Bitcoin Price Forecasting using `Dataprep`

## Table of Contents

This markdown follows a hierarchical TOC and guideline structure as outlined in the course template.

### Hierarchy


## General Guidelines

This notebook follows the guidelines in [README](/DATA605/DATA605_Spring2025/README.md) and is structured to demonstrate the use of `Dataprep` for time series analysis.

---

# Project Description

This project implements a complete system to ingest, clean, explore, and forecast real-time Bitcoin price data. It demonstrates the use of `Dataprep` for streamlining the data preparation and exploratory data analysis processes, particularly in a big data time series context.

# Technology Stack

- `Dataprep`: For data cleaning (`clean_headers`, `clean_text`) and EDA (`plot`, `plot_correlation`, `plot_missing`, `create_report`)
- `Pandas`: For time series indexing and data manipulation
- `Statsmodels`: For ARIMA modeling
- `pmdarima`: For Auto-ARIMA selection
- `Matplotlib`: For custom visualizations and forecast plotting

# Architecture & Workflow

1. Ingest real-time Bitcoin data (pre-collected from CoinGecko)
2. Clean the dataset using `Dataprep.clean` and `pandas`
3. Perform visual and statistical EDA using `Dataprep.eda`
4. Apply time series models (ARIMA & Auto-ARIMA)
5. Plot forecast results with timestamp alignment and confidence intervals

# API/DataSource

- Public data source: CoinGecko Bitcoin price API (pre-ingested CSV)
- Tools: `requests`, `pandas` for collection and storage

# Data Cleaning

- `clean_headers()` for standardizing column names
- `clean_text()` applied to a sample text column to demonstrate non-numeric cleaning
- Used `pandas.to_datetime()` and `to_numeric()` for type conversions

# Exploratory Data Analysis

- Used `Dataprep.eda.plot()` for distribution of `price_usd`
- Used `plot_missing()` to verify data completeness
- Used `create_report()` to generate a comprehensive HTML EDA summary

# Time Series Modeling

- Manual ARIMA(5,1,0): Fit and forecast Bitcoin price using `statsmodels`
- Auto-ARIMA: Optimal model selection using `pmdarima.auto_arima()`
- Evaluated RMSE for both models
- Generated future forecasts for 100 time steps

# Visualization and Interpretation

- Historical vs forecasted prices plotted with aligned timestamps
- Forecasts visualized side-by-side (manual vs auto)
- Auto-ARIMA forecast includes confidence intervals shaded in red
- All plots labeled, formatted, and grid-aligned for readability

# Key Insights and Results

- Manual ARIMA RMSE: ~27.33  
- Auto-ARIMA RMSE: ~26.66  
- Forecasts are stable and trend-preserving
- DataPrep significantly accelerated EDA and helped reveal skewness, gaps, and data quality insights instantly

# Conclusion

This project successfully demonstrates the power and simplicity of `Dataprep` in cleaning, profiling, and visualizing real-time Bitcoin price data. Combined with traditional modeling, it provides a scalable framework for time series forecasting in financial datasets.

