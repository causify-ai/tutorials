# Time Series Analysis of Bitcoin Prices Using Scikit-learn

## Project Description

In this project, I wanted to explore how machine learning could be applied to financial time series data. I chose Bitcoin due to its dynamic nature and accessibility of real-time data. Using the CoinGecko API, I pulled historical price data and applied a simple linear regression model to predict future prices.

## Data and API Integration

I used the CoinGecko API to fetch daily Bitcoin price data for the past 365 days. The API response includes timestamps and prices, which I converted into a structured format using pandas. This raw data was then prepared for machine learning through normalization and shifting the target values.

## Machine Learning Workflow

- **Preprocessing**: I cleaned the data, handled missing values, and used Scikit-learn’s `StandardScaler` to normalize the features.
- **Training**: I split the data into training and testing sets using `train_test_split` and trained a linear regression model.
- **Evaluation**: I evaluated the model using mean squared error and R2 score to assess accuracy.
- **Visualization**: Finally, I visualized the predictions alongside the actual values to interpret the results clearly.

## Project Structure

- The entire ML pipeline was modularized into functions and stored in `utils.py`.
- The analysis was run from `Bitcoin_Price_TSA_Updated.ipynb` using those modular functions.
- API integration and parsing was handled separately in `api.ipynb`.

## Conclusion

This project helped me understand how to integrate an external API with a machine learning pipeline. It also reinforced the importance of data preprocessing and evaluation when working with time series forecasting problems.
