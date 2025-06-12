# BTC_SQLAlchemy.example.md

## Project Overview

This project demonstrates a real-time Bitcoin price analysis and forecasting pipeline using:
- CoinGecko’s public API
- SQLAlchemy for local database management
- Pandas and scikit-learn for feature engineering and modeling

The goal is to capture Bitcoin price data, store it in a structured database, engineer time-series features, and build predictive models to forecast short-term price movements.

---

## Problem Statement

Bitcoin is a highly volatile asset, and its short-term price movements are of interest to traders and analysts. This project builds a system to:

- Ingest real-time and historical Bitcoin prices
- Store the data locally using SQLAlchemy
- Engineer relevant time-series features
- Train models to predict the next time step’s price

---

## Data Flow and Technology Stack

**Ingestion:**  
- CoinGecko API is used to fetch:
  - Real-time snapshot (`fetch_price`)
  - Historical 30-day hourly prices (`fetch_30day_price_series`)
  - 5-minute streaming prices (`fetch_realtime_5min_series`)

**Storage:**  
- SQLite database using SQLAlchemy ORM
- Data inserted using `save_price` and `save_price_series`
- Data retrieved with `load_data_from_db`

**Feature Engineering:**  
- Percentage returns (`price.pct_change`)
- Lagged features (`lag_1`, `lag_2`)
- 7-period rolling average and standard deviation
- Temporal features: hour of day, day of week
- Target: next-step price (`shift(-1)`)

**Modeling:**  
- Linear Regression (interpretable baseline)
- Random Forest Regressor (nonlinear benchmark)

**Evaluation Metrics:**  
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² (Coefficient of Determination)

---

## Key Results

**Linear Regression:**
- MAE: $136.82
- RMSE: $221.06
- R²: 0.7277

**Random Forest Regressor:**
- MAE: $182.05
- RMSE: $268.96
- R²: 0.5969

Linear regression outperformed the random forest, indicating that the current feature set is well-suited for linear models under this dataset size.

---

## Design Decisions

- SQLAlchemy was used over raw SQL for clean schema definition and modularity.
- Historical and live ingestion pipelines are separate but integrated via common interfaces.
- Data deduplication was implemented before insertion.
- The model was trained using a time-aware (chronological) split to preserve the sequence of observations.

---

## Final Notes

This end-to-end notebook shows how a real-world machine learning pipeline can be structured using open APIs, local databases, and interpretable models. The system is modular, reusable, and easy to extend with additional features, models, or data sources in the future.
