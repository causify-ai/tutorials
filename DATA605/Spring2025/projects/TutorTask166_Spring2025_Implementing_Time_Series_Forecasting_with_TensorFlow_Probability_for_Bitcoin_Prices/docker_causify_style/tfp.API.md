<!-- toc -->

- [TensorFlow Probability API for Bitcoin Price Forecasting](#tensorflow-probability-api-for-bitcoin-price-forecasting)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [Core Components](#core-components)
    + [Structural Time Series Models](#structural-time-series-models)
    + [Bayesian Inference Methods](#bayesian-inference-methods)
    + [Forecasting with Uncertainty](#forecasting-with-uncertainty)
  * [Key Classes and Functions](#key-classes-and-functions)
    + [BitcoinForecastModel](#bitcoinforecastmodel)
    + [Preprocessing Functions](#preprocessing-functions)
    + [Evaluation Metrics](#evaluation-metrics)

<!-- tocstop -->

# TensorFlow Probability API for Bitcoin Price Forecasting

This document describes the TensorFlow Probability (TFP) API used for Bitcoin price forecasting in this project. The implementation leverages TFP's structural time series modeling capabilities to create robust forecasts with uncertainty quantification.

## Table of Contents

The document is organized to cover the core components of the TensorFlow Probability API used in this project, including model structure, inference methods, and forecasting approaches.

### Hierarchy

```
# Level 1 (Used as title)
## Level 2
### Level 3
```

## Core Components

### Structural Time Series Models

TensorFlow Probability provides a flexible framework for building structural time series models through the `tfp.sts` module. Our Bitcoin price forecasting model uses the following components:

1. **Local Linear Trend**: Captures the primary price movement direction and acceleration
2. **Seasonal Components**: Models daily and weekly patterns in cryptocurrency trading
3. **Autoregressive Components**: Captures short-term dependencies in price movements
4. **Special Cryptocurrency Components**: Custom components for modeling volatility clusters

The components are combined using `tfp.sts.Sum` to create a comprehensive model that can capture the complex dynamics of cryptocurrency prices.

### Bayesian Inference Methods

The project implements two primary inference methods:

1. **Variational Inference (VI)**: Used for faster model fitting, especially in real-time applications
   - Implemented using `tfp.vi.fit_surrogate_posterior`
   - Uses adaptive learning rates and early stopping for efficient convergence

2. **Markov Chain Monte Carlo (MCMC)**: Used for more accurate parameter estimation when time permits
   - Implemented using `tfp.mcmc.sample_chain`
   - Hamiltonian Monte Carlo with step size adaptation

### Forecasting with Uncertainty

One of the key advantages of using TensorFlow Probability is the ability to generate forecasts with uncertainty intervals:

1. **Posterior Predictive Sampling**: Generates multiple forecast trajectories
2. **Uncertainty Quantification**: Provides lower and upper bounds for price predictions
3. **Ensemble Methods**: Combines multiple forecasting approaches for improved accuracy

## Key Classes and Functions

### BitcoinForecastModel

The core class for Bitcoin price forecasting with the following key methods:

- `__init__(config)`: Initializes the model with configuration parameters
- `preprocess_data(data)`: Prepares time series data for modeling
- `build_model(observed_time_series)`: Constructs the structural time series model
- `fit(observed_time_series)`: Performs inference to learn model parameters
- `forecast(num_steps)`: Generates forecasts with uncertainty intervals
- `evaluate_prediction(actual_price, prediction)`: Calculates error metrics
- `update(new_data_point)`: Updates the model with new observations

### Preprocessing Functions

Functions for preparing data for the model:

- `preprocess_price_data(data)`: Handles outliers and normalizes price data
- `detect_price_anomalies(price_series)`: Identifies anomalous price movements
- `preprocess_price_series(price_series)`: Comprehensive preprocessing pipeline

### Evaluation Metrics

Methods for assessing forecast quality:

- `evaluate_prediction(actual_price, prediction)`: Calculates error metrics
- `adaptive_forecast(time_series)`: Simple forecasting for comparison
- `ensemble_forecast(time_series)`: Combines multiple forecasting methods 