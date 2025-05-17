"""
Bitcoin Price Forecasting with TensorFlow Probability - Example Implementation.

1. This example demonstrates how to use the TensorFlow Probability API for Bitcoin price forecasting
   with the following key features:
   - Loading and preprocessing Bitcoin price data
   - Building and training a structural time series model
   - Generating forecasts with uncertainty intervals
   - Evaluating prediction accuracy

2. References:
   - TensorFlow Probability API: See tfp.API.md for detailed documentation
   - Original research: Durbin & Koopman (2012). Time Series Analysis by State Space Methods.

This script demonstrates the practical usage of the Bitcoin forecasting API in a real-world scenario.
The example loads historical Bitcoin price data, trains a model, and generates forecasts.

Follow the reference on coding style guide to write clean and readable code.
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import logging
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union, Optional, Any

# Import the Bitcoin forecast model
from tfp.API import BitcoinForecastModel

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
_LOG = logging.getLogger(__name__)


def load_bitcoin_data(data_path: str, lookback_days: int = 30) -> pd.DataFrame:
    """
    Load historical Bitcoin price data from CSV file.
    
    :param data_path: Path to the CSV data file
    :param lookback_days: Number of days of historical data to load
    :return: DataFrame with Bitcoin price data
    """
    _LOG.info("Loading Bitcoin price data from %s", data_path)
    
    try:
        # Load data from CSV
        df = pd.read_csv(data_path)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Filter to lookback period
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        df = df[df['timestamp'] >= cutoff_date]
        
        _LOG.info("Loaded %d records from %s to %s", 
                 len(df), 
                 df['timestamp'].min().strftime('%Y-%m-%d'),
                 df['timestamp'].max().strftime('%Y-%m-%d'))
        
        return df
    
    except Exception as e:
        _LOG.error("Error loading data: %s", str(e))
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['timestamp', 'price'])


def preprocess_data(df: pd.DataFrame) -> np.ndarray:
    """
    Preprocess Bitcoin price data for model input.
    
    :param df: DataFrame with Bitcoin price data
    :return: Numpy array with preprocessed price data
    """
    _LOG.info("Preprocessing data for model input")
    
    try:
        # Check if DataFrame is empty
        if df.empty:
            _LOG.warning("Empty DataFrame provided for preprocessing")
            return np.array([])
        
        # Extract price column
        prices = df['price'].values
        
        # Handle missing values
        if np.isnan(prices).any():
            _LOG.info("Handling %d missing values", np.isnan(prices).sum())
            # Simple forward fill for missing values
            last_valid = prices[0]
            for i in range(len(prices)):
                if np.isnan(prices[i]):
                    prices[i] = last_valid
                else:
                    last_valid = prices[i]
        
        return prices
    
    except Exception as e:
        _LOG.error("Error preprocessing data: %s", str(e))
        return np.array([])


def plot_forecast(actual_prices: np.ndarray, 
                 forecast_mean: float, 
                 forecast_lower: float, 
                 forecast_upper: float,
                 title: str = "Bitcoin Price Forecast") -> None:
    """
    Plot actual prices and forecast with uncertainty interval.
    
    :param actual_prices: Array of historical prices
    :param forecast_mean: Mean forecast value
    :param forecast_lower: Lower bound of forecast interval
    :param forecast_upper: Upper bound of forecast interval
    :param title: Plot title
    :return: None
    """
    plt.figure(figsize=(12, 6))
    
    # Plot historical data
    x_hist = np.arange(len(actual_prices))
    plt.plot(x_hist, actual_prices, 'b-', label='Historical Prices')
    
    # Plot forecast point
    x_forecast = len(actual_prices)
    plt.plot(x_forecast, forecast_mean, 'ro', label='Forecast')
    
    # Plot uncertainty interval
    plt.fill_between([x_forecast], [forecast_lower], [forecast_upper], 
                    color='r', alpha=0.2, label='95% Confidence Interval')
    
    # Add labels and legend
    plt.xlabel('Time Steps')
    plt.ylabel('Bitcoin Price (USD)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Show the plot
    plt.tight_layout()
    plt.show()


def evaluate_forecast(actual_value: float, 
                     forecast_mean: float, 
                     forecast_lower: float, 
                     forecast_upper: float) -> Dict[str, float]:
    """
    Evaluate forecast accuracy and uncertainty calibration.
    
    :param actual_value: Actual observed price
    :param forecast_mean: Mean forecast value
    :param forecast_lower: Lower bound of forecast interval
    :param forecast_upper: Upper bound of forecast interval
    :return: Dictionary with evaluation metrics
    """
    # Calculate error metrics
    error = actual_value - forecast_mean
    abs_error = abs(error)
    pct_error = (abs_error / actual_value) * 100 if actual_value != 0 else float('inf')
    
    # Check if actual value is within confidence interval
    in_interval = forecast_lower <= actual_value <= forecast_upper
    interval_width = forecast_upper - forecast_lower
    
    # Compile metrics
    metrics = {
        'absolute_error': abs_error,
        'percentage_error': pct_error,
        'in_confidence_interval': in_interval,
        'confidence_interval_width': interval_width
    }
    
    return metrics


def main() -> None:
    """
    Main function to demonstrate Bitcoin price forecasting.
    """
    _LOG.info("Starting Bitcoin price forecasting example")
    
    # Define paths and parameters
    data_path = os.path.join('data', 'bitcoin_prices.csv')
    config = {
        'model': {
            'variational_steps': 100,
            'learning_rate': 0.05,
            'forecast_steps': 1,
            'outlier_threshold': 3.0,
            'ar_order': 1,
            'use_mixed_precision': False
        }
    }
    
    # Load and preprocess data
    df = load_bitcoin_data(data_path)
    prices = preprocess_data(df)
    
    if len(prices) == 0:
        _LOG.error("No valid data available. Exiting.")
        return
    
    # Split data into training and test sets
    train_size = int(0.8 * len(prices))
    train_data = prices[:train_size]
    test_data = prices[train_size:]
    
    _LOG.info("Training data: %d points, Test data: %d points", 
             len(train_data), len(test_data))
    
    # Initialize and train the model
    model = BitcoinForecastModel(config)
    model.fit(train_data)
    
    # Generate forecast
    forecast_mean, forecast_lower, forecast_upper = model.forecast()
    
    _LOG.info("Forecast: %.2f (%.2f, %.2f)", 
             forecast_mean, forecast_lower, forecast_upper)
    
    # Evaluate forecast against the next actual value
    if len(test_data) > 0:
        actual_next_value = test_data[0]
        metrics = evaluate_forecast(actual_next_value, 
                                   forecast_mean, 
                                   forecast_lower, 
                                   forecast_upper)
        
        _LOG.info("Evaluation metrics:")
        for metric, value in metrics.items():
            _LOG.info("  %s: %s", metric, value)
        
        # Plot results
        plot_forecast(train_data, forecast_mean, forecast_lower, forecast_upper)
    else:
        _LOG.warning("No test data available for evaluation")


if __name__ == "__main__":
    main() 