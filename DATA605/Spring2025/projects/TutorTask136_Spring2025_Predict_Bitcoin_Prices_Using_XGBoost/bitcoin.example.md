# Bitcoin Price Prediction with XGBoost

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Datasets Used](#2-datasets-used)
3. [Feature Engineering](#3-feature-engineering)
4. [Model and Evaluation](#4-model-and-evaluation)
5. [Project Structure](#5-project-structure)
6. [Running with Docker](#6-running-with-docker)
7. [Results and Insights](#7-results-and-insights)
8. [References](#8-references)
9. [Author](#9-author)

## 1. Project Overview

This project demonstrates an end-to-end workflow for forecasting daily Bitcoin prices using the XGBoost regression algorithm. Instead of directly predicting price, the model learns to predict daily returns, from which price is reconstructed.

The analysis compares short-term vs long-term historical data sources and evaluates performance using error metrics such as MAE and RMSE.

## 2. Datasets Used

- **CoinGecko API**: Limited to 365 days of historical data. Suitable for small-scale experimentation.
- **Yahoo Finance (BTC-USD)**: Covers 10 years of daily Bitcoin prices, providing a richer dataset for training more robust models.

## 3. Feature Engineering

Features derived from historical closing prices:
- **Lag Features**: Return from previous 1 to 3 days.
- **Rolling Statistics**: Moving averages and standard deviations over 3-day and 7-day windows.
- **Temporal Features**: Day of the week, and month of the year.

Target Variable:
- One-day forward return (`return_1d`), used to reconstruct prices.

## 4. Model and Evaluation

Model:
- XGBoost Regressor (`reg:squarederror`)

Evaluation Metrics:
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Squared Error

Model trained using an 80/20 train-test split and tested via both static and real-time simulations.

## 5. Project Structure

```
bitcoin_price_xgboost/
├── bitcoin.example.ipynb            # Main notebook for full analysis
├── bitcoin.API.ipynb                # Data collection from APIs
├── bitcoin_utils.py                 # Feature engineering and helper functions
├── BTC-USD-Historical.xlsx          # Yahoo Finance data dump
└── docker_data605_style/
    ├── docker_build.sh              # Script to build Docker container
    ├── docker_jupyter.sh            # Script to run Jupyter inside container
    └── Dockerfile                   # Docker build configuration
```

## 6. Running with Docker

This project is Docker-ready via a preconfigured environment.

### Prerequisites
- Docker installed on your machine
- Bash terminal

### Steps to Run

```bash
# Navigate to the root directory
cd DATA605/Spring2025/projects/TutorTask136_Spring2025_Predict_Bitcoin_Prices_Using_XGBoost/docker_scripts_with_python_files

# Step 1: Build Docker image
chmod +x docker_build.sh
./docker_build.sh
Step2: run the bash bash script
chmod +x docker_bash.sh
./docker_bash.sh
# Step 3: Launch Jupyter Notebook server
./run_jupyter.sh
./docker_jupyter.sh
```

Access Jupyter at `http://localhost:8888/` and open the `bitcoin.example.ipynb` notebook.

## 7. Results and Insights

| Dataset        | MAE        | RMSE       |
|----------------|------------|------------|
| CoinGecko (1y) | 10,523.48  | 11,506.02  |
| Yahoo (10y)    | 7,096.99   | 9,432.30   |

Key insights:
- More data history (Yahoo) resulted in better generalization and forecasting ability.
- Daily returns are noisy and hard to predict; compounding errors affect price reconstruction.
- Short-term models underperform due to volatility and limited historical context.

## 8. References

- CoinGecko API: https://www.coingecko.com/en/api
- Yahoo Finance (yfinance): https://pypi.org/project/yfinance/
- XGBoost: https://xgboost.readthedocs.io/en/stable/

## 9. Author

## 9. Author

**maruti kameshwar**  
Graduate Student, University of Maryland  

