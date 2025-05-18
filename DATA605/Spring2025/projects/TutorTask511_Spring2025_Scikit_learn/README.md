# Time Series Analysis of Bitcoin Prices Using Scikit-learn

This project focuses on analyzing and forecasting Bitcoin price trends using machine learning techniques. Specifically, I used Scikit-learn to build a linear regression model that predicts future Bitcoin prices based on historical data. The dataset is obtained from the CoinGecko API, and the process involves several steps including data acquisition, preprocessing, training, evaluation, and visualization.

## Project Components

- `Bitcoin_Price_TSA_Updated.ipynb`: This is the main notebook where I demonstrate the entire pipeline using reusable functions from the `utils.py` module.
- `api.ipynb`: This notebook is focused on explaining how I accessed and processed data from the CoinGecko API.
- `utils.py`: A Python module that contains all the necessary functions such as data fetching, preprocessing, training, evaluating, and plotting.
- `scikit_learn.API.md`: Documentation explaining how the CoinGecko API is used in this project.
- `scikit_learn.example.md`: Detailed explanation of how the entire project was structured and implemented.

## Dependencies

To run this project, install the following Python packages:

```bash
pip install pandas numpy matplotlib scikit-learn requests
```

## Running the Project

1. Use `api.ipynb` to understand how the Bitcoin data is fetched and processed from the API.
2. Run `Bitcoin_Price_TSA_Updated.ipynb` to execute the full analysis pipeline using functions from `utils.py`.

## Purpose

This project helped me understand the basics of time series analysis, model training and evaluation using Scikit-learn, and working with public APIs for real-time data collection.
