#!/usr/bin/env python3
"""
TensorFlow Probability model for Bitcoin price forecasting.
Implements a structural time series model with local linear trend and seasonal components.
"""
import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np
from datetime import datetime, timedelta

tfd = tfp.distributions
tfs = tfp.sts

class BitcoinForecastModel:
    def __init__(self, num_timesteps=60, num_seasons=24):
        """
        Initialize the Bitcoin forecast model.
        
        Args:
            num_timesteps: Number of timesteps to use for prediction
            num_seasons: Number of seasonal components (24 for hourly seasonality)
        """
        self.num_timesteps = num_timesteps
        self.num_seasons = num_seasons
        self.model = None
        self.posterior = None
        self.observed_time_series = None
        
        # Set default dtype to float64 for all tensors
        tf.keras.backend.set_floatx('float64')
        
    def build_model(self, observed_time_series):
        """
        Build the structural time series model.
        
        Args:
            observed_time_series: Tensor of observed Bitcoin prices
        """
        # Convert input to float64
        observed_time_series = tf.cast(observed_time_series, tf.float64)
        
        # Local linear trend component
        local_linear_trend = tfs.LocalLinearTrend(
            observed_time_series=observed_time_series
        )
        
        # Seasonal component (hourly seasonality)
        seasonal = tfs.Seasonal(
            num_seasons=self.num_seasons,
            observed_time_series=observed_time_series
        )
        
        # Combine components
        self.model = tfs.Sum(
            components=[local_linear_trend, seasonal],
            observed_time_series=observed_time_series
        )
        
        return self.model
    
    def fit(self, observed_time_series, num_variational_steps=100):
        """
        Fit the model to the observed time series.
        
        Args:
            observed_time_series: Tensor of observed Bitcoin prices
            num_variational_steps: Number of optimization steps
        """
        if self.model is None:
            self.build_model(observed_time_series)
        
        # Convert to tensor and ensure float64
        self.observed_time_series = tf.cast(observed_time_series, tf.float64)
        
        # Build surrogate posterior
        surrogate = tfs.build_factored_surrogate_posterior(model=self.model)
        
        # Define joint log probability function
        def target_log_prob_fn(**params):
            return self.model.joint_distribution(
                observed_time_series=self.observed_time_series
            ).log_prob(**params)
        
        # Fit the surrogate posterior
        losses = tfp.vi.fit_surrogate_posterior(
            target_log_prob_fn=target_log_prob_fn,
            surrogate_posterior=surrogate,
            optimizer=tf.optimizers.Adam(learning_rate=0.1),
            num_steps=num_variational_steps
        )
        
        self.posterior = surrogate
        return surrogate
    
    def forecast(self, num_steps=1):
        """
        Generate forecasts for future timesteps.
        
        Args:
            num_steps: Number of steps to forecast ahead
            
        Returns:
            Tuple of (mean forecast, lower bound, upper bound)
        """
        if self.posterior is None:
            raise ValueError("Model must be fit before forecasting")
        
        # Sample from the posterior
        samples = self.posterior.sample(100)
        
        # Generate forecasts
        forecast_dist = tfs.forecast(
            model=self.model,
            observed_time_series=self.observed_time_series,
            parameter_samples=samples,
            num_steps_forecast=num_steps
        )
        
        # Calculate mean and confidence intervals
        mean = forecast_dist.mean()
        stddev = forecast_dist.stddev()
        
        # 95% confidence interval
        lower_bound = mean - 1.96 * stddev
        upper_bound = mean + 1.96 * stddev
        
        # Convert back to float32 for compatibility with other parts of the system
        return float(mean[-1]), float(lower_bound[-1]), float(upper_bound[-1])
    
    def update(self, new_observation):
        """
        Update the model with a new observation.
        
        Args:
            new_observation: New Bitcoin price observation
        """
        # Convert to tensor and ensure float64
        new_observation = tf.cast(new_observation, tf.float64)
        
        # Update model with new observation
        self.fit(new_observation, num_variational_steps=10) 