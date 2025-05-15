# Bitcoin Price Forecasting Model Documentation

## Overview

This document provides a comprehensive overview of the Bitcoin price forecasting application implemented using TensorFlow Probability (TFP). The system provides real-time price predictions with uncertainty estimates using structural time series models and Bayesian inference techniques.

## Model Architecture

The Bitcoin forecasting model uses a structural time series approach based on TensorFlow Probability. The core architecture consists of multiple components combined to capture various aspects of Bitcoin price movements:

1. **Local Linear Trend**: Models the underlying trend in Bitcoin prices, allowing for both level (the current value) and slope (the direction and rate of change) to evolve over time. This component helps capture the overall direction of price movements.

2. **Seasonal Component**: Captures regular cyclical patterns in Bitcoin trading activity that might occur over specific time intervals (e.g., daily, weekly). The implementation uses a configurable number of seasons to adapt to different time frequencies.

3. **Autoregressive Component**: Models short-term dependencies where current prices depend on recent past prices. The model uses a higher-order AR(3) model when enough data is available, which captures more complex patterns than a standard AR(1) model.

## Inference Techniques

The model uses two primary Bayesian inference techniques:

### 1. Variational Inference (VI)

The primary inference method used is Variational Inference, which approximates the posterior distribution over model parameters. This technique:

- Is computationally efficient for real-time forecasting
- Uses TensorFlow's optimization capabilities for fast convergence
- Adapts learning rates based on recent forecast errors
- Employs a custom learning rate scheduler with warmup and decay phases

### 2. Markov Chain Monte Carlo (MCMC)

For scenarios requiring more accurate uncertainty estimates, the model can fall back to MCMC sampling:

- Uses Hamiltonian Monte Carlo for efficient sampling in high-dimensional parameter spaces
- Employs step size adaptation during burnin phase to improve convergence
- Maintains sample chains that better represent the full posterior distribution
- Automatically falls back to VI if MCMC fails or is too slow

## Input Processing Pipeline

The model takes raw Bitcoin price data and processes it through several stages:

1. **Data Loading**: Historical data is loaded from CSV files with configurable window sizes
2. **Preprocessing**: 
   - Timestamp normalization and conversion
   - Missing value handling
   - Outlier detection and handling using interquartile range (IQR) method
   - Technical indicators calculation (when enabled)
   - Data scaling and transformation

## Forecasting Process

The forecasting process follows these steps:

1. **Model Building**: Components are constructed and combined into a structural time series model
2. **Parameter Inference**: Bayesian inference is performed to estimate parameter distributions
3. **Forecast Generation**: Future predictions are made by sampling from the posterior predictive distribution
4. **Uncertainty Quantification**: 95% confidence intervals are calculated based on the forecast distribution
5. **Evaluation**: The model evaluates its predictions against actual prices when they become available

## Adaptive Learning

The model incorporates several adaptive learning techniques:

1. **Continuous Model Updates**: New observations are incorporated to update the model's internal state
2. **Variable Learning Rates**: The optimizer adjusts learning rates based on recent prediction errors
3. **Anomaly Detection**: The model flags anomalous predictions using z-score methods
4. **Dynamic VI Steps**: The number of variational inference steps adjusts based on price volatility
5. **Model Reinitialization**: The system can detect and recover from TensorFlow variable errors

## Fallback Mechanisms

The system includes multiple fallback mechanisms for robustness:

1. **Robust Prediction**: If the main model fails, a simpler statistical approach is used
2. **Last Forecast Reuse**: When computing resources are constrained, previous forecasts can be reused
3. **Error Handling**: Comprehensive error catching and recovery at multiple levels
4. **Model Version Tracking**: The system tracks model versions to aid in debugging

## Performance Metrics

The model tracks several performance metrics:

1. **Mean Absolute Error (MAE)**: Average of absolute differences between predictions and actual prices
2. **Percentage Error**: Relative error as a percentage of the actual price
3. **Z-scores**: Standardized errors for anomaly detection
4. **Standard Deviation**: Uncertainty in predictions from the posterior distribution
5. **Root Mean Square Error (RMSE)**: Square root of the average of squared differences between predictions and actual prices

### Note on MAE Chart

The MAE chart shows frequent fluctuations because it represents the absolute error for each individual prediction point, not a rolling or cumulative average. Each point on the chart is the absolute error |actual - predicted| for a single timestamp. Since Bitcoin prices can be volatile, and the model must constantly adapt to new market conditions, the errors naturally fluctuate from prediction to prediction.

## Implementation Details

The model is implemented in Python using several key libraries:

- **TensorFlow Probability**: Core modeling and inference engine
- **NumPy**: Numerical computations and array handling
- **Pandas**: Data manipulation and analysis
- **Kafka**: Real-time data ingestion
- **Dash/Plotly**: Interactive visualization dashboard

The implementation follows a modular design with separation of concerns:

- **Model**: Core TFP model implementation
- **Data Processing**: Data loading, preprocessing, and validation
- **Prediction Service**: Real-time prediction generation
- **Dashboard**: Interactive visualization of predictions and metrics

## Deployment Architecture

The application is deployed as a set of Docker containers:

1. **Bitcoin Forecast App**: Ingests data, runs the model, and produces predictions
2. **Dashboard**: Visualizes predictions and performance metrics
3. **Kafka**: Message broker for real-time data streams
4. **Zookeeper**: Manages Kafka cluster configuration

## Conclusion

The Bitcoin forecasting model combines modern Bayesian methods with structural time series modeling to provide real-time price predictions with quantified uncertainty. Its adaptive learning capabilities and robust fallback mechanisms make it suitable for the highly volatile cryptocurrency market environment. 