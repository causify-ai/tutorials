# Bitcoin Price Time Series Analysis

This project implements a time series analysis model for Bitcoin price prediction using historical data from the CoinGecko API.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the following files in your project directory:
- `utils.py`: Contains all the utility functions for data fetching, preprocessing, and model training
- `Bitcoin_Price_TSA_Updated.ipynb`: The main Jupyter notebook that runs the analysis

## Features

- Fetches historical Bitcoin price data from CoinGecko API
- Preprocesses data with various technical indicators:
  - Previous day prices
  - Rolling averages (3-day and 7-day)
  - Day of week features
- Implements a Linear Regression model for price prediction
- Includes visualization of actual vs predicted prices

## Usage

1. Open `Bitcoin_Price_TSA_Updated.ipynb` in Jupyter Notebook or JupyterLab
2. Run the cells in sequence to:
   - Fetch Bitcoin price data
   - Preprocess the data
   - Train the model
   - Evaluate the results
   - Visualize predictions

## Note

The CoinGecko API has rate limits. If you encounter any issues with data fetching, you may need to wait a few minutes before trying again.