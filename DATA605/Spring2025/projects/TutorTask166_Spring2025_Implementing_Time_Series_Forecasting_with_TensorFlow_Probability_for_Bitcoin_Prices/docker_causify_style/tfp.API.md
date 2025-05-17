<!-- toc -->

- [TensorFlow Probability API for Bitcoin Price Forecasting](#tensorflow-probability-api-for-bitcoin-price-forecasting)
  - [Table of Contents](#table-of-contents)
    - [Overview](#overview)
    - [Core Components](#core-components)
      - [Structural Time Series Models](#structural-time-series-models)
      - [Bayesian Inference Methods](#bayesian-inference-methods)
      - [Forecasting with Uncertainty](#forecasting-with-uncertainty)
    - [Key Classes and Functions](#key-classes-and-functions)
      - [BitcoinForecastModel](#bitcoinforecastmodel)
      - [Preprocessing Utilities](#preprocessing-utilities)
      - [Evaluation Metrics](#evaluation-metrics)
    - [API Tutorial & Usage](#api-tutorial--usage)
      - [General Guidelines](#general-guidelines)
      - [Example Workflow](#example-workflow)
      - [Code Snippet](#code-snippet)

<!-- tocstop -->

# TensorFlow Probability API for Bitcoin Price Forecasting

This document unifies the API reference and usage tutorial for our Bitcoin price-forecasting system, built on TensorFlow Probability (TFP). It covers model design, inference techniques, data preprocessing, and practical examples.

## Overview

We leverage TFP’s **structural time series** framework to capture trends, seasonality, and short‐term autocorrelations in Bitcoin prices. Two Bayesian inference methods provide a balance between real‐time performance and parameter accuracy:

- **Variational Inference (VI)** for fast, online updates  
- **Markov Chain Monte Carlo (MCMC)** for deeper parameter exploration  

Forecasts include uncertainty intervals, and an ensemble approach smooths out individual run variability.

## Core Components

### Structural Time Series Models

Our model composes several `tfp.sts` components via `Sum`:

1. **Local Linear Trend**  
2. **Seasonal** (daily, weekly, custom frequency)  
3. **Autoregressive** (short‐term dependencies)  
4. **Semi‐Local Trend** (captures volatility clusters)  

### Bayesian Inference Methods

- **Variational Inference**  
  - `tfp.vi.fit_surrogate_posterior`  
  - Adaptive learning rate schedules, dynamic step counts  

- **MCMC (Hamiltonian Monte Carlo)**  
  - `tfp.mcmc.sample_chain`  
  - Step‐size adaptation during burn-in  

### Forecasting with Uncertainty

- **Posterior Predictive Sampling**: multiple trajectories  
- **Confidence Intervals**: e.g., 95% or 99% bounds  
- **Ensemble Averaging**: combine several forecast draws  

## Key Classes and Functions

### BitcoinForecastModel

Encapsulates model lifecycle:

```python
class BitcoinForecastModel:
    def __init__(self, config):
        """
        Initialize model parameters and inference settings.

        :param config: dict of model settings (learning_rate, vi_steps, num_samples, etc.)
        """
    def preprocess_data(self, data: np.ndarray) -> tf.Tensor:
        """
        Clean and enhance raw price series.

        :param data: 1D numpy array of historical prices
        :return: float64 Tensor of the cleaned series
        """
    def build_model(self, observed_time_series: tf.Tensor) -> tfp.sts.Sum:
        """
        Assemble structural time series components.

        :param observed_time_series: tensor of historical prices
        :return: TFP Sum model
        """
    def fit(self, observed_time_series: np.ndarray) -> Any:
        """
        Run VI or MCMC to fit model parameters.

        :param observed_time_series: raw price array
        :return: trained posterior
        """
    def forecast(self, num_steps: int = 1) -> Tuple[float, float, float]:
        """
        Generate point forecast plus lower/upper bounds.

        :param num_steps: forecast horizon
        :return: (mean, lower_bound, upper_bound)
        """
    def evaluate_prediction(self, actual_price: float, prediction: float) -> dict:
        """
        Compute MAE, percentage error, z-score, anomaly flag.

        :param actual_price: true price
        :param prediction: forecasted mean
        :return: dict of metrics
        """
    def update(self, new_data_point: float) -> bool:
        """
        Incorporate one new observation and refit lightly.

        :param new_data_point: latest price
        :return: success flag
        """

```

Preprocessing Utilities
	•	Outlier handling via modified Z-score, IQR, percentage jumps
	•	Technical indicators: moving averages, RSI, MACD, Bollinger Bands
	•	Normalization: robust scaling (median / IQR)

Evaluation Metrics
	•	Mean Absolute Error (MAE)
	•	Percentage Error
	•	Z-score (for anomaly detection)

⸻

### API Tutorial & Usage

This section illustrates a typical workflow.

General Guidelines
	1.	Prepare configuration: choose lookback window, inference steps
	2.	Instantiate model: pass your config dict
	3.	Load historical data: numpy array of closing prices
	4.	Fit: train VI or MCMC posterior
	5.	Forecast: obtain prediction + interval
	6.	Evaluate: compare against actual

Notebook: tfp.API.ipynb contains a step-by-step guide with cell outputs.

### Example Workflow
	1.	Import & configure
	2.	Fit on historical series
	3.	Loop
	•	Forecast for next second
	•	Save prediction & metrics
	•	Append actual price via update()

### Code Snippet

```python
from tfp_API import BitcoinForecastModel
import numpy as np

# 1. Load or define your config
config = {
    'model': {
        'instant': {
            'lookback': 60,
            'vi_steps': 100,
            'num_samples': 50,
            'learning_rate': 0.01
        }
    }
}

# 2. Initialize
model = BitcoinForecastModel(config)

# 3. Fit on past price series
historical_prices = np.load('btc_prices.npy')  # e.g., shape (n,)
model.fit(historical_prices)

# 4. Make a forecast
mean, lower, upper = model.forecast(num_steps=1)
print(f"Forecast: {mean:.2f} [{lower:.2f}, {upper:.2f}]")

# 5. After observing actual price:
actual = 103500.0
metrics = model.evaluate_prediction(actual, mean)
print("Metrics:", metrics)

# 6. Update model with actual
model.update(actual)
```

For more details and advanced usage, see [`tfp.API.ipynb`](./tfp.API.ipynb). 