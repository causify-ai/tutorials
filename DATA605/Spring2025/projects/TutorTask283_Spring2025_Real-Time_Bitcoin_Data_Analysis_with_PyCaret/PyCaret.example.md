

# Bitcoin Price Forecasting Project Using PyCaret

This notebook demonstrates a complete end-to-end workflow to fetch, process, model, and visualize Bitcoin price data using the PyCaret time series module. The entire analysis leverages reusable utility functions encapsulated in the `PyCaret_utils.py` module, ensuring concise and maintainable code.

---

## 1. Importing Required Modules and Utilities

The notebook starts by importing necessary Python libraries and functions from the `PyCaret_utils.py` module. The modular import ensures that complex logic is abstracted away, allowing this notebook to focus on demonstrating the project workflow cleanly.
These functions encapsulate complex operations into single callable units, improving code readability and modularity. Key functions used include:

CoinGeckoAPI(): A class that wraps CoinGecko’s REST API to simplify the process of fetching OHLC cryptocurrency data.

fetch_and_validate_data(api_obj, days=90): Fetches the last N days of hourly Bitcoin price data, cleans missing values, converts timestamps, and adds derived metrics.

prepare_data_for_pycaret(df): Structures the dataframe specifically for PyCaret—ensures correct index, sorts chronologically, and filters the appropriate target column.

run_pycaret_experiment(df): Initializes and configures the PyCaret time series experiment environment for modeling.

add_lag_features(df): Adds lagged versions of the target variable as new columns for feature engineering.

---

## 2. Fetching and Preparing Bitcoin Data

Using the `CoinGeckoAPI` class, the notebook fetches historical OHLC (Open, High, Low, Close) data for Bitcoin priced in USD over the last 90 days. This class handles API communication, including error handling and rate limiting.

The raw OHLC data is then passed through `fetch_and_validate_data()`, which performs several critical steps:

* **Validation:** Checks that the returned data is a non-empty DataFrame with all required OHLC columns.
* **Cleaning:** Removes any duplicate timestamps to maintain data integrity.
* **Feature Engineering:** Adds calculated columns including:

  * **daily\_return:** The percentage change in closing price compared to the previous time interval.
  * **volatility\_7d:** The rolling standard deviation of daily returns over a 7-day window, quantifying short-term price fluctuations.
  * **volume\_ema\_14:** An exponential moving average of the closing price over 14 periods, smoothing out noise to identify trends.

This processed dataset forms the foundation for subsequent modeling.

---

## 3. Preparing Data for PyCaret Experiment

The `prepare_data_for_pycaret()` function formats the data specifically for PyCaret's time series modeling requirements. This includes:

* Selecting the ‘close’ price column as the target variable.
* Resampling the data to ensure a consistent daily frequency, forward-filling any missing dates to maintain continuity.
* Removing any remaining missing values to prevent errors during model training.

Ensuring a clean, continuous, and properly indexed dataset is crucial for reliable time series forecasting.

---

## 4. Setting up the PyCaret Time Series Experiment

The core modeling process is initiated with `run_pycaret_experiment(data)`. This function:

* Configures PyCaret's time series experiment by specifying the target column (`close`).
* Defines an expanding window cross-validation strategy with three folds, which simulates training on progressively larger portions of historical data and tests on subsequent periods.
* Applies forward-fill imputation to handle any remaining missing values in the target.
* Fixes a random seed to ensure reproducibility of results.
* Sets the forecasting horizon to 7 days, instructing models to predict one week into the future.

This setup enables PyCaret to automatically preprocess data, tune models, and evaluate forecasting performance using consistent parameters.

---

## 5. Comparing and Selecting the Best Model

The notebook calls `compare_models()`, which internally trains multiple state-of-the-art forecasting algorithms on the prepared dataset, including models such as ARIMA, Prophet, and various machine learning regressors.

PyCaret ranks these models by their forecasting accuracy metrics (e.g., Mean Absolute Error), allowing identification of the best-performing model on the validation sets. The output displays the model type and performance summary, informing the user which approach works best for this dataset.

---

## 6. Finalizing and Saving the Best Model

Once the optimal model is identified, `finalize_model(best_model)` retrains it on the entire dataset, consolidating learned patterns for deployment.

The notebook then demonstrates saving this finalized model to disk using `save_model()`. Persisting the model allows it to be reloaded later without retraining, saving computation time and enabling reproducible forecasting.

---

## 7. Forecasting Future Bitcoin Prices

Using `predict_model(final_model)`, the notebook generates 7-day forecasts based on the finalized model. The output includes predicted closing prices for each day in the forecast horizon, along with confidence intervals if available.

These predictions provide actionable insights into expected Bitcoin price trends in the immediate future.

---

## 8. Visualizing Historical and Forecasted Prices

Visualization is a key part of analysis. The notebook creates an interactive Plotly figure combining:

* The historical closing price series as a continuous line.
* The forecasted prices as lines with markers.

This dual plot allows visual comparison of past trends and future predictions. The graph’s layout is customized with titles and axis labels, using a dark theme for clarity.

Such visualization aids in understanding model behavior and communicating results effectively.

---

## 9. Auto-Regressive Feature Engineering (Lag Features)

To capture the intrinsic temporal dependencies in Bitcoin price movements, the notebook applies the `add_lag_features()` function.

This function creates new columns for lagged closing prices at multiple previous time points. For example:

* **lag\_1:** The closing price one time step (e.g., one hour or one day) before the current observation.
* **lag\_2:** The closing price two time steps earlier.
* **lag\_n:** Similarly for the nth previous time step.

These lag features explicitly encode recent historical values, enabling models to learn how past prices influence current and future prices. Such auto-regressive inputs often enhance model accuracy by making temporal patterns explicit rather than implicit.

The notebook displays the last few rows of this enriched dataset, demonstrating the added features.

---

## 10. Model Export and Reuse

After training and evaluating, the notebook shows how to save the model using `save_model()`. This function serializes the model object to disk in a format compatible with PyCaret.

Later, the model can be restored with `load_model()`, allowing users to generate forecasts without re-running the training pipeline.

This practice supports efficient deployment and reproducibility in real-world applications.

---

## 11. Project Workflow Visualization

To summarize the entire forecasting pipeline, the notebook builds a directed graph illustrating the sequence of key steps using NetworkX and Matplotlib:

* Fetching raw OHLC data from the API.
* Validating and cleaning the data.
* Engineering features such as returns and lag values.
* Setting up and running the PyCaret experiment.
* Comparing multiple forecasting models.
* Finalizing the best model.
* Predicting future Bitcoin prices.
* Visualizing the forecast results.

Each step is represented as a node, with arrows indicating the process flow. The graph provides a high-level overview of the project structure, useful for presentations or documentation.

---




## 12.Visualizing Moving Averages for Trend Analysis

To enhance interpretability and identify short- and mid-term trends in Bitcoin price data, we calculate and plot **moving averages** alongside the original closing prices. This step adds an additional layer of analysis useful for understanding the general direction of the market and smoothing out short-term volatility.

We compute two commonly used moving averages:

* A **7-day moving average (MA\_7)** that captures short-term price movements.
* A **14-day moving average (MA\_14)** that provides a mid-term view of the trend.

The result is a visually appealing and information-rich chart that makes it easy to spot:

* Crossovers between the short-term and long-term trends.
* Potential inflection points where momentum might be shifting.
* Periods of consolidation or breakout based on divergence between moving averages.

# Summary

This notebook walks through the entire process of Bitcoin price forecasting using PyCaret, starting from data acquisition to producing actionable forecasts and visualizations. Each function from the utility module is leveraged to maintain modularity and readability. The approach incorporates best practices such as feature engineering, model comparison, and persistence, making it suitable for both academic and production use cases.




