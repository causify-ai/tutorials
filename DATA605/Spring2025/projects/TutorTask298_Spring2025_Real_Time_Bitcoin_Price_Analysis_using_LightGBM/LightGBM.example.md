# LightGBM Real-Time Bitcoin Forecasting Example

This example demonstrates how to build and evaluate a real-time Bitcoin price prediction pipeline using the LightGBM machine learning model. It is based on real data from the CoinGecko API and is structured for clarity, modularity, and educational purposes.

##  Objective

To fetch, process, and forecast Bitcoin prices using a LightGBM model, and visualize the actual vs. predicted results to understand the model's accuracy in real-world data ingestion scenarios.

## Components Used

- **Data Source:** CoinGecko public API for Bitcoin price data.
- **Model:** LightGBM Regressor (via `lightgbm` Python package).
- **Metrics:** RMSE, MAE.
- **Visualization:** Matplotlib.
- **Feature Engineering:** Lag values, time-based components, rolling statistics.

##  Workflow Overview

1. **Fetch Bitcoin Prices:**  
   Use CoinGecko’s historical price API to retrieve Bitcoin price data for the past 30 days at frequent intervals.

2. **Preprocess Data:**  
   Engineer time-based features such as:
   - Hour, minute, day of week
   - Lag values (1-step, 2-step)
   - Rolling mean and std deviation

3. **Train LightGBM Model:**  
   Train the LightGBM model to learn from historical features and forecast the next price point.

4. **Evaluate Model:**  
   Assess model accuracy using RMSE and MAE. Plot the predicted vs. actual price trend.

5. **Visualize Results:**  
   Generate a time-indexed plot comparing predicted values to actual market prices to validate performance.

##  Utility Functions

All logic is wrapped inside a reusable `LightGBM_utils.py` file to maintain clean notebooks. Functions include:

- `fetch_bitcoin_data()`
- `create_features()`
- `train_lightgbm()`
- `evaluate_model()`
- `plot_predictions()`

##  Key Observations

- Model performs reasonably well in short-term prediction with minimal lag.
- LightGBM handled the time-series features efficiently even with minimal tuning.
- Small rolling windows (e.g., 3 periods) captured short-term fluctuations effectively.

## Future Enhancements

- Integrate **live streaming** via `websocket-client` for true real-time ingestion.
- Add hyperparameter tuning (e.g., GridSearchCV).
- Try more complex features (e.g., trend lines, macroeconomic indicators).
- Incorporate early stopping with validation data.

## 🔗References

- [LightGBM Official Docs](https://lightgbm.readthedocs.io/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api)
- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Matplotlib Documentation](https://matplotlib.org/)