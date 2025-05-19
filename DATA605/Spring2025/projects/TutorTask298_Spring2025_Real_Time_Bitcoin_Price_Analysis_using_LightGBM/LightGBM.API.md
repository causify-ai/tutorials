LightGBM.API.markdown file

<!-- toc -->
- [LightGBM.example.md](#lightgbmexamplemd)
- [Project Summary](#project-summary)
- [General Guidelines](#general-guidelines)
- [About LightGBM](#about-lightgbm)
- [API Overview](#api-overview)
  - [fetch_bitcoin_data](#fetch_bitcoin_data)
  - [create_features](#create_features)
  - [train_lightgbm](#train_lightgbm)
  - [evaluate_model](#evaluate_model)
  - [plot_predictions](#plot_predictions)
- [Citations and References](#citations-and-references)
- [Future Improvements](#future-improvements)
- [Additional APIs to Explore](#additional-apis-to-explore)
<!-- tocstop -->


# LightGBM.example.md

TutorTask298_Spring2025_Real_Time_Bitcoin_Price_Analysis_using_LightGBM

## Project Summary

This project builds a real-time Bitcoin price forecasting pipeline using LightGBM. It pulls historical price data from the CoinGecko API, performs lag- and time-based feature engineering, trains a LightGBM regressor, and evaluates the model using standard error metrics and visual diagnostics. The structure supports modular expansion and real-time integration.

## General Guidelines

This markdown file documents the API layer built for using LightGBM in the context of real-time Bitcoin price forecasting.

- Each function is modular and meant to be reused across projects.
- Code for these APIs lives in `LightGBM_utils.py`.
- They are demonstrated in `LightGBM.API.ipynb`.

## About LightGBM

LightGBM is a fast, distributed, high-performance gradient boosting framework based on decision tree algorithms, used for ranking, classification, and many other machine learning tasks.

- Designed by Microsoft.
- Optimized for large-scale datasets.
- Offers categorical feature support and faster training.

## API Overview

### fetch_bitcoin_data

Fetches historical Bitcoin prices from CoinGecko for a given number of days (default: 30).

- Input: `days=30`
- Output: Pandas DataFrame with timestamp and price columns.

### create_features

Transforms raw price data into a feature-rich dataset.

- Adds time-based features: minute, hour, day of week.
- Includes lag variables and rolling statistics.
- Returns a DataFrame ready for model training.

### train_lightgbm

Trains a LightGBM regression model.

- Input: feature-rich DataFrame.
- Output: Trained LightGBM model, `X_test`, `y_test`.

### evaluate_model

Evaluates the model using RMSE and MAE.

- Returns:
  - Root Mean Squared Error
  - Mean Absolute Error
  - Actual values (`y_test`) and predictions (`y_pred`)

### plot_predictions

Plots actual vs predicted prices.

- Input: `y_test`, `y_pred`
- Output: Matplotlib plot with time-indexed visualization.

## Citations and References

- [LightGBM Official Documentation](https://lightgbm.readthedocs.io/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)

## Future Improvements

- Integrate real-time streaming via WebSockets.
- Add hyperparameter tuning with Optuna or GridSearchCV.
- Include GPU acceleration support.
- Store predictions in a time-series database.

## Additional APIs to Explore

- `lightgbm.Dataset()` for advanced model configuration.
- `lightgbm.cv()` for cross-validation.
- Real-time APIs from Binance or CryptoCompare for live streaming data.
