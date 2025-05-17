
# API Notebook Explained (API.ipynb)


## Introduction to Facebook Prophet

Facebook Prophet is an open-source time series forecasting tool developed by Meta’s Core Data Science team. It is highly effective for financial time series such as Bitcoin prices, where capturing complex seasonality, trend shifts, and market anomalies is critical.

### **Why Use Prophet?**

* Automatically detects and models trends and seasonality.
* Handles missing data and outliers gracefully.
* Provides uncertainty intervals for predictions.
* Allows modeling of special events (e.g., Bitcoin halving events).
* Generates highly interpretable plots and visualizations.

---

## Functional Workflow

### load\_historical\_data(filepath)

* Loads historical Bitcoin price data from a CSV file.
* Formats columns for Prophet (`ds` for date, `y` for closing price).

### fetch\_live\_data(days, currency)

* Fetches the latest Bitcoin price data from the CoinGecko API.
* Returns data formatted for Prophet compatibility.

### merge\_and\_clean\_data(historical\_df, live\_df)

* Merges historical and real-time Bitcoin data.
* Removes duplicates and ensures continuous, clean time series data.

### create\_prophet\_model()

* Initializes a Facebook Prophet model with predefined settings.
* Includes custom seasonality, changepoint detection, and holiday events like Bitcoin halvings.

###  train\_prophet\_model(model, df)

* Trains the Prophet model on the merged Bitcoin dataset.
* Prepares the model for accurate forecasting.

###  make\_forecast(model, periods)

* Generates future Bitcoin price predictions for a specified period.
* Returns forecasted values along with confidence intervals.

###  plot\_forecast(model, forecast)

* Plots forecasted Bitcoin prices using Prophet’s visualization tools.
* Displays trends, seasonality components, and prediction intervals.

### Evaluation Metrics (RMSE, MAE)

* Calculates and reports **RMSE** (Root Mean Squared Error) and **MAE** (Mean Absolute Error).
* Evaluates the predictive accuracy of the model against actual price data.

### Changepoint Detection

* Visualizes changepoints detected by the model.
* Highlights significant shifts in Bitcoin price trends influenced by market events.

---

##  Conclusion

This notebook demonstrates how to perform Bitcoin price forecasting using historical and real-time data with Facebook Prophet.

* The trained model effectively captured trend changes, seasonal patterns, and significant market events.
* Visualizations clearly show future forecasts along with uncertainty intervals, helping users interpret the results confidently.
* Evaluation metrics validate that the model performs well even in highly volatile financial markets like Bitcoin.
* Using Prophet simplifies complex time series forecasting and offers interpretable, actionable insights for financial decision-making.

