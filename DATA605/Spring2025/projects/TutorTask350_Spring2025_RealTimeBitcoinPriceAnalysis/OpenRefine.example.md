 <!-- toc -->

* [Project Title](#project-title)

  * [Table of Contents](#table-of-contents)
  * [Project Summary](#project-summary)
  * [Technology & Tools Used](#technology-&-tools-used)
  * [File Layout](#file-layout)
  * [Execution Instructions](#execution-instructions)
  * [Data Collection](#data-collection)
  * [Analysis Techniques](#analysis-techniques)
  * [Function Descriptions](#function-descriptions)

<!-- tocstop -->

# OpenRefine.example.md

TutorTask350\_Spring2025\_Real-time\_Bitcoin\_Price\_Analysis\_with\_OpenRefine

## Project Summary

This project demonstrates how to clean and prepare real-time Bitcoin price data using OpenRefine and Python, followed by time series analysis and forecasting. The data is fetched from the KuCoin API at 15-minute intervals, cleaned via OpenRefine, enriched with technical indicators in Python, and finally forecasted using Prophet.

## Technology & Tools Used

* OpenRefine for data cleaning and transformation
* KuCoin API for real-time Bitcoin price data
* Pandas for data manipulation
* Plotly and Matplotlib for interactive visualizations
* Prophet for time series forecasting
* Python 3.10 as the core programming language

## File Layout

* The project directory includes:

  * `openrefine_utils.py`: reusable helper functions
  * `OpenRefine.API.ipynb`: demonstrates API logic and utility functions
  * `OpenRefine.example.ipynb`: full example applying the API to real data
  * `bitcoin_15m_kucoin.csv`: pre-cleaned raw data
  * `bitcoin_price_analysis_using_OpenRefine_w_timestamp`: OpenRefine-cleaned dataset (With Timestamps)
  * `bitcoin_price_analysis_using_OpenRefine_notimestamp.csv`: OpenRefine-cleaned dataset (Without Timestamps)
  * All visualizations and forecast results are generated within the example notebook

## Execution Instructions

1. Start Docker and OpenRefine locally.
2. Fetch Bitcoin data using `fetch_bitcoin_data_kucoin()`.
3. Clean and transform the data in OpenRefine.
4. Export the cleaned CSV file.
5. Load the cleaned data into the example notebook using `load_cleaned_data()`.
6. Run the cells to compute indicators, resample, validate, and forecast.

## Data Collection

Data is collected using the KuCoin Klines API, which returns 15-minute OHLCV Bitcoin price data. This data includes open, high, low, close, volume, and timestamps for each interval.

The data is fetched via a utility script and stored as a CSV file for OpenRefine preprocessing.

## Analysis Techniques

The analysis methodology includes:

* Validation of cleaned data extracted by OpenRefine using logical checks for double check.
* Resampling the data into hourly and daily aggregates. This is done solely to improve our understanding and interpretation of the trends and this resampled data is not used for modeling; the original 15-minute interval Bitcoin data is used for all subsequent analysis and forecasting.
* Calculating additional technical indicators and adding them to the 15-minute interval data. Used technical indicators:

  * Moving Averages (7, 24)
  * Bollinger Bands
  * Volatility & Momentum
* Forecasting next 24 hours using Prophet.
* Visualizing actual vs predicted prices, confidence intervals, volume, and trends.


## Function Descriptions

* **fetch\_bitcoin\_data\_kucoin()**

  * Connects to the KuCoin API and fetches recent Bitcoin OHLCV data at 15-minute intervals.
  * Returns a DataFrame containing timestamped open, high, low, close, and volume values.

* **save\_to\_csv()**

  * Saves any DataFrame into a CSV file with the specified path and filename.
  * Used to store raw or cleaned datasets for later processing or OpenRefine use.

* **load\_cleaned\_data()**

  * Loads the dataset cleaned in OpenRefine for further use in the notebook.
  * Ensures the correct schema is preserved and data types are appropriately parsed.

* **validate\_cleaned\_data()**

  * Checks for missing values, time consistency, and logical price constraints.
  * Logs results and flags errors to prevent inaccurate downstream analysis.

* **resample\_data()**

  * Converts raw 15-minute interval data to hourly or daily frequency for aggregation.
  * Supports cleaner trend analysis and better forecasting granularity.

* **calculate\_technical\_indicators()**

  * Computes 7-period and 24-period moving averages, Bollinger Bands, and momentum.
  * Adds columns to the DataFrame for use in trend and volatility visualizations to better undrestand the current data.

* **plot\_technical\_indicators()**

  * Creates a static line plot showing the closing price, moving averages, and Bollinger Bands.
  * Helps visualize price trends and volatility zones clearly.

* **prepare\_forecast\_data()**

  * Prepares the cleaned dataset in the structure required for Prophet forecasting.
  * Renames columns to 'ds' and 'y' and formats timestamps.

* **train\_model()**

  * Trains a Prophet time series model on the historical Bitcoin data.
  * Configures forecasting horizon and generates the future DataFrame.

* **plot\_forecast()**

  * Generates an interactive Plotly chart showing actual vs predicted prices.
  * Includes confidence intervals and properly labeled time and price axes.

* **plot\_comparision()**

  * Merges actual and forecasted results and plots them together interactively.
  * Shows actual, predicted, and confidence interval bands for side-by-side comparison.












