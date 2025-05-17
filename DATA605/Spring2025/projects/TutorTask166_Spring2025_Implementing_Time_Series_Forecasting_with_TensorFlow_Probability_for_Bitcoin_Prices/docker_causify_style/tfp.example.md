<!-- toc -->

- [Bitcoin Price Forecasting with TensorFlow Probability](#bitcoin-price-forecasting-with-tensorflow-probability)
  - [Table of Contents](#table-of-contents)
    - [Overview](#overview)
    - [Architecture](#architecture)
    - [Implementation Details](#implementation-details)
      - [Data Pipeline](#data-pipeline)
      - [Model Structure](#model-structure)
      - [Forecasting Process](#forecasting-process)
    - [Results and Evaluation](#results-and-evaluation)
    - [API Tutorial & Example](#api-tutorial--example)
      - [General Guidelines](#general-guidelines)
      - [Example Workflow](#example-workflow)
      - [Code Snippet](#code-snippet)
      - [Demonstration](#demonstration)

<!-- tocstop -->

# Bitcoin Price Forecasting with TensorFlow Probability

A real-time system for forecasting Bitcoin prices using TensorFlow Probability’s structural time series models, with uncertainty quantification, anomaly detection, and continuous learning.

## Overview

This project ingests live Bitcoin market data, preprocesses it (outliers, technical indicators), fits a probabilistic time series model (local trends, seasonality, autoregression), and produces per-second forecasts with confidence intervals. Predictions and metrics are exposed via a web dashboard.

## Architecture

1. **Data Collector**  
   Streams raw price ticks into CSV/Kafka.  
2. **Forecast Engine**  
   `BitcoinForecastApp` loads data, invokes `BitcoinForecastModel` (TFP), saves predictions & metrics.  
3. **Web Dashboard**  
   Visualizes live forecasts, error metrics, and anomalies.  
4. **Kafka & Zookeeper**  
   Ensures robust, decoupled communication between services.  
5. **Containerization**  
   Docker Compose orchestrates four services: data-collector, forecast-app, web-app, Kafka/Zookeeper.

## Implementation Details

### Data Pipeline

1. **Collection**: Exchange data → CSV/Kafka  
2. **Preprocessing**:  
   - Outlier detection (modified Z-score, IQR, % jumps)  
   - Technical indicators (MA, EMA, RSI, MACD, Bollinger Bands)  
   - Robust scaling (median/IQR)  
3. **Feature Engineering**: Windowed lookback and seasonality features  

### Model Structure

Built with `tfp.sts` components combined via `Sum`:

- **Local Linear Trend** (level & slope)  
- **Seasonal** (daily/weekly patterns)  
- **Autoregressive** (short-term dependencies)  
- **Semi-Local Trend** (volatility clusters)  

Inference methods:

- **Variational Inference** (`tfp.vi.fit_surrogate_posterior`)  
- **MCMC** (`tfp.mcmc.sample_chain`, HMC with step-size adaptation)  

### Forecasting Process

1. **Initialization**: Load config (lookback, vi_steps, num_samples, learning_rate)  
2. **Fit**: VI or MCMC on historical tensor  
3. **Forecast**: Posterior predictive sampling → mean & interval  
4. **Evaluate**: MAE, % error, z-score (anomaly flag)  
5. **Update**: Append new price → light refit → continuous learning  

## Results and Evaluation

Metrics tracked per timestamp:

- **MAE** (Mean Absolute Error)  
- **RMSE** (Root Mean Square Error)  
- **Confidence Interval Coverage**  
- **Anomaly Detection Rate**  

Empirical tests show <0.2 MAE on per-second data and robust interval calibration.

---

# API Tutorial & Example

A concise guide to using the core forecasting API in your own code.

## General Guidelines

- Follow the [project README](./README.md) for setup.  
- Import `BitcoinForecastModel` from `tfp_API.py`.  
- Use Jupyter notebooks (`tfp.API.ipynb`, `tfp.example.ipynb`) for interactive exploration.

## Example Workflow

1. **Define Config**: Specify lookback, seasons, learning rate, VI steps, sample count.  
2. **Initialize Model**:
```python
from tfp_API import BitcoinForecastModel
model = BitcoinForecastModel(config)
```
3.	**Fit on Historical Data**:
```python
model.fit(price_series)  # price_series: np.ndarray of closing prices
```
4.	**Forecast**:
```python
mean, lower, upper = model.forecast(num_steps=1)
```
5.	**Evaluate**:
```python
metrics = model.evaluate_prediction(actual_price, mean)
```
6.	**Update**:
```python
model.update(new_price)
```

##	**Code Snippet**:
```python
import numpy as np
from tfp_API import BitcoinForecastModel

# 1. Sample configuration
config = {
    'model': {
        'instant': {
            'lookback': 30,
            'num_seasons': 24,
            'learning_rate': 0.01,
            'vi_steps': 100,
            'num_samples': 50
        }
    }
}

# 2. Instantiate & fit
model = BitcoinForecastModel(config)
prices = np.load('btc_prices.npy')  # historical prices
model.fit(prices)

# 3. Forecast next step
mean, lower, upper = model.forecast()
print(f"Next price: {mean:.2f} [{lower:.2f}, {upper:.2f}]")

# 4. Evaluate on observed price
actual = prices[-1]
metrics = model.evaluate_prediction(actual, mean)
print("Error metrics:", metrics)

# 5. Update with latest price
new_price = 103550.0
model.update(new_price)
```

## Demonstration

- The example demonstrates the full workflow: data loading, model fitting, forecasting, and evaluation.
- Results include the predicted price, confidence interval, and error metrics.
- For more details and visualizations, see [`tfp.example.ipynb`](./tfp.example.ipynb). 