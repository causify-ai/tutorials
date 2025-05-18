<!-- toc -->

- [Project Title](#project-title)
  * [Table of Contents](#table-of-contents)
    + [Structure Guide](#structure-guide)
  * [Project Summary](#project-summary)
  * [Technology Stack](#technology-stack)
  * [File Layout](#file-layout)
  * [Execution Instructions](#execution-instructions)
  * [Data Collection](#data-collection)
  * [Analysis Techniques](#analysis-techniques)
  * [Best Practices](#best-practices)
  * [Future Enhancements](#future-enhancements)
  * [Key Observations](#key-observations)
  * [References](#references)

<!-- tocstop -->

# LightGBM.example.md

TutorTask298_Spring2025_Real_Time_Bitcoin_Price_Analysis_using_LightGBM

---

## Project Summary

This project builds a real-time Bitcoin price forecasting system using LightGBM. It combines live data ingestion from CoinGecko with time-based and statistical feature engineering. The model is trained using historical data and continuously improved with recent data. The system supports real-time prediction, performance evaluation, and visualization of trends and anomalies.

The design emphasizes modularity and future extensibility — for example, incorporating other coins, tuning models, or integrating streaming data sources.

---

## Technology Stack

- **LightGBM**: For fast gradient boosting regression
- **scikit-learn**: For data splitting and evaluation metrics
- **Pandas**: For data manipulation and feature engineering
- **Matplotlib + Seaborn**: For visualizations
- **Requests**: For fetching live and historical Bitcoin price data via CoinGecko
- **Python 3.11**

---

## File Layout

The project structure is as follows:

- `LightGBM_utils.py`: Core utility functions (data ingestion, feature creation, evaluation, visualization)
- `LightGBM.API.ipynb`: Documents and tests the reusable API layer (no training here)
- `LightGBM.example.ipynb`: Full real-time forecasting pipeline and evaluation
- `bitcoin_data.csv`: Stores historical or live Bitcoin prices (optional cache)
- `README.md`, `.gitignore`: Environment hygiene and reproducibility

---

## Execution Instructions

To run the forecasting system:

1. Clone the repository and set up a Python virtual environment.
2. Install required libraries from `requirements.txt`.
3. Run `LightGBM.example.ipynb` end-to-end:
   - Fetch historical + real-time data
   - Generate time/lag-based features
   - Train LightGBM model
   - Evaluate with RMSE and MAE
   - Forecast and visualize

The notebook supports both batch training and single-point prediction (e.g., for live dashboards).

---

## Data Collection

Bitcoin price data is retrieved from the CoinGecko API in two ways:

- **Historical Data**: Fetched via `/market_chart`, returns hourly or daily prices
- **Real-Time Price**: Fetched via `/simple/price`, returns the latest price

A utility function (`get_combined_bitcoin_data`) allows merging both sources into a single dataset for model training and prediction.

---

## Analysis Techniques

The project applies machine learning and statistical techniques:

- **Feature Engineering**:
  - Lagged prices (`lag_1`, `lag_2`)
  - Rolling mean and standard deviation (window = 3)
  - Time-based features: hour, minute, day of week
- **Modeling**:
  - LightGBM regression with training/test split
  - Real-time prediction using latest available features
- **Evaluation**:
  - RMSE and MAE for overall test performance
  - Real-time RMSE and MAE for the most recent prediction
- **Visualization**:
  - Actual vs predicted price line chart
  - Prediction error distribution
  - Moving average and anomaly overlays (Z-score)

---
##  Key Observations

- Model performs reasonably well in short-term prediction with minimal lag.
- LightGBM handled the time-series features efficiently even with minimal tuning.
- Small rolling windows (e.g., 3 periods) captured short-term fluctuations effectively.

---

## Best Practices

- All logic is modularized in `LightGBM_utils.py` for reuse and testing
- Real-time forecasting is separate from batch evaluation
- Model evaluation includes both traditional metrics and visual diagnostics
- Code avoids hardcoding window sizes or file paths for flexibility
- Live API calls are abstracted behind clearly named functions
- Error handling is included for empty data, missing prices, and invalid API responses

This setup supports a scalable forecasting system that can evolve into a dashboard, alerting system, or multi-asset crypto predictor.

---
## Future Enhancements

- Integrate **live streaming** via `websocket-client` for true real-time ingestion.
- Add hyperparameter tuning (e.g., GridSearchCV).
- Try more complex features (e.g., trend lines, macroeconomic indicators).
- Incorporate early stopping with validation data.

---

## 🔗 References

- [LightGBM Official Docs](https://lightgbm.readthedocs.io/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api)
- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Matplotlib Documentation](https://matplotlib.org/)