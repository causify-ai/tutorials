#!/usr/bin/env python3
"""
TensorFlow Probability model for Bitcoin price forecasting.
Implements a structural time series model with local linear trend and seasonal components.
"""
import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np
from datetime import datetime, timedelta
import gc
import traceback
import os

tfd = tfp.distributions
tfs = tfp.sts

class BitcoinForecastModel:
    def __init__(self, config):
        """
        Initialize the Bitcoin forecast model.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.service_name = os.environ.get('SERVICE_NAME', 'bitcoin_forecast_app')
        
        # Get model config from the service-specific section directly
        model_config = None
        
        # Check if service-specific config exists at top level and has model section
        if self.service_name in self.config and 'model' in self.config[self.service_name]:
            model_config = self.config[self.service_name]['model']['instant']
            print(f"Using service-specific model config from top level")
        else:
            # Fallback to global model config if service-specific not found
            model_config = self.config.get('model', {}).get('instant', {})
            print(f"Using fallback global model config")
        
        # If we still don't have a valid config, use defaults
        if not model_config:
            print(f"No model config found, using defaults")
            model_config = {}
        
        self.num_timesteps = model_config.get('lookback', 60)
        self.num_seasons = model_config.get('num_seasons', 24)
        self.model = None
        self.posterior = None
        self.observed_time_series = None
        
        # Set default dtype to float64 for all tensors
        tf.keras.backend.set_floatx('float64')
        
        # Store the learning rate from config
        self.learning_rate = model_config.get('learning_rate', 0.01)
        
        # Get VI steps from config
        self.vi_steps = model_config.get('vi_steps', 100)
        
        # Store num_samples for forecasting
        self.num_samples = model_config.get('num_samples', 50)
        
        # Track model rebuilds
        self.model_version = 0
        
        # Last forecast values (for fallback)
        self.last_forecast = None
        self.last_mean = None
        self.last_lower = None
        self.last_upper = None
        
        # Debug log
        print(f"Initialized model with num_samples={self.num_samples}, vi_steps={self.vi_steps}")

    def _create_optimizer(self):
        """Create a fresh optimizer instance."""
        return tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        
    def build_model(self, observed_time_series):
        """
        Build the structural time series model.
        
        Args:
            observed_time_series: Tensor of observed Bitcoin prices
        """
        try:
            # Convert input to float64 tensor
            observed_time_series = tf.convert_to_tensor(observed_time_series, dtype=tf.float64)
            
            # Create priors with explicit float64 dtype
            level_scale_prior = tfd.LogNormal(
                loc=tf.constant(0., dtype=tf.float64),
                scale=tf.constant(1., dtype=tf.float64)
            )
            slope_scale_prior = tfd.LogNormal(
                loc=tf.constant(0., dtype=tf.float64),
                scale=tf.constant(1., dtype=tf.float64)
            )
            initial_level_prior = tfd.Normal(
                loc=observed_time_series[0],
                scale=tf.constant(1000., dtype=tf.float64)
            )
            initial_slope_prior = tfd.Normal(
                loc=tf.constant(0., dtype=tf.float64),
                scale=tf.constant(100., dtype=tf.float64)
            )
            
            # Local linear trend component with explicit float64 priors
            local_linear_trend = tfs.LocalLinearTrend(
                observed_time_series=observed_time_series,
                level_scale_prior=level_scale_prior,
                slope_scale_prior=slope_scale_prior,
                initial_level_prior=initial_level_prior,
                initial_slope_prior=initial_slope_prior
            )
            
            # Create seasonal prior with explicit float64 dtype
            drift_scale_prior = tfd.LogNormal(
                loc=tf.constant(0., dtype=tf.float64),
                scale=tf.constant(1., dtype=tf.float64)
            )
            
            # Seasonal component with explicit float64 prior
            seasonal = tfs.Seasonal(
                num_seasons=self.num_seasons,
                observed_time_series=observed_time_series,
                drift_scale_prior=drift_scale_prior
            )
            
            # Combine components
            model = tfs.Sum(
                components=[local_linear_trend, seasonal],
                observed_time_series=observed_time_series
            )
            
            # Clear any old model resources
            if self.model is not None:
                del self.model
                gc.collect()
                
            self.model = model
            self.model_version += 1
            return model
            
        except Exception as e:
            print(f"Error building model: {e}\n{traceback.format_exc()}")
            return None
    
    def fit(self, observed_time_series, num_variational_steps=None):
        """
        Fit the model to the observed time series.
        
        Args:
            observed_time_series: Tensor of observed Bitcoin prices
            num_variational_steps: Number of optimization steps (optional, uses config if None)
        """
        try:
            # Use provided steps or fall back to config
            if num_variational_steps is None:
                num_variational_steps = self.vi_steps
            
            # Build a new model or rebuild if needed
            if self.model is None:
                self.build_model(observed_time_series)
            
            # Convert to tensor and ensure float64
            self.observed_time_series = tf.convert_to_tensor(observed_time_series, dtype=tf.float64)
            
            # Clear old TF variables by creating a new surrogate posterior
            # Build surrogate posterior - this creates new TF variables
            surrogate = tfs.build_factored_surrogate_posterior(model=self.model)
            
            # Create a new optimizer for each fit to prevent variable sharing issues
            optimizer = self._create_optimizer()
            
            # Define joint log probability function
            def target_log_prob_fn(**params):
                return self.model.joint_distribution(
                    observed_time_series=self.observed_time_series
                ).log_prob(**params)
            
            # Fit the surrogate posterior with a fresh optimizer
            losses = tfp.vi.fit_surrogate_posterior(
                target_log_prob_fn=target_log_prob_fn,
                surrogate_posterior=surrogate,
                optimizer=optimizer,  # Fresh optimizer
                num_steps=num_variational_steps
            )
            
            # Explicitly clear the old posterior to release memory
            if self.posterior is not None:
                del self.posterior
                gc.collect()
                
            self.posterior = surrogate
            return surrogate
            
        except Exception as e:
            print(f"Error fitting model: {e}\n{traceback.format_exc()}")
            return None
    
    def forecast(self, num_steps=1):
        """
        Generate forecasts for future timesteps.
        
        Args:
            num_steps: Number of steps to forecast ahead
            
        Returns:
            Tuple of (mean forecast, lower bound, upper bound)
        """
        try:
            # Log that we're making a forecast
            print(f"[{datetime.now().isoformat()}] Making forecast with TFP model v{self.model_version}")
            
            if self.posterior is None:
                if self.last_forecast is not None:
                    print("Using last forecast as fallback")
                    return self.last_mean, self.last_lower, self.last_upper
                
                # For cold start when we have no posterior or previous forecast,
                # use a more intelligent estimate based on the observed data
                if self.observed_time_series is not None:
                    # Use the last observed value as the prediction
                    data = self.observed_time_series.numpy()
                    mean_val = float(data[-1])
                    
                    # Calculate standard deviation from recent data for confidence interval
                    if len(data) >= 5:
                        std = float(np.std(data[-5:]))
                    else:
                        std = float(mean_val * 0.005)  # 0.5% of mean as std
                    
                    # Create confidence interval (95%)
                    lower_val = mean_val - 1.96 * std
                    upper_val = mean_val + 1.96 * std
                    
                    # Store for future use
                    self.last_mean = mean_val
                    self.last_lower = lower_val
                    self.last_upper = upper_val
                    self.last_forecast = {
                        'mean': mean_val,
                        'lower': lower_val,
                        'upper': upper_val
                    }
                    
                    print(f"Making cold start prediction using last observed value: {mean_val}")
                    return mean_val, lower_val, upper_val
                
                raise ValueError("Model must be fit before forecasting")
            
            # Use the stored num_samples from init instead of accessing config again
            samples = self.posterior.sample(self.num_samples)
            
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
            
            # Convert to float for consistency
            mean_val = float(mean[-1])
            lower_val = float(lower_bound[-1])
            upper_val = float(upper_bound[-1])
            
            # Store the forecast for fallback
            self.last_mean = mean_val
            self.last_lower = lower_val
            self.last_upper = upper_val
            self.last_forecast = {
                'mean': mean_val,
                'lower': lower_val,
                'upper': upper_val
            }
            
            return mean_val, lower_val, upper_val
            
        except Exception as e:
            print(f"Error in forecast: {e}\n{traceback.format_exc()}")
            # Fallback to last forecast if available
            if self.last_forecast is not None:
                print("Using last forecast as fallback after error")
                return self.last_mean, self.last_lower, self.last_upper
            
            # Intelligence fallback if we have data
            if self.observed_time_series is not None:
                data = self.observed_time_series.numpy()
                # Use the last observed value with a small confidence interval
                mean_val = float(data[-1])
                std = float(np.std(data)) if len(data) > 1 else float(mean_val * 0.005)
                lower_val = mean_val - 1.96 * std
                upper_val = mean_val + 1.96 * std
                
                print(f"Using intelligence fallback after error: {mean_val} (±{std})")
                return mean_val, lower_val, upper_val
            
            # Last resort fallback with market-reasonable values
            # Bitcoin price is typically in the $50,000-100,000 range
            recent_avg = 103000.0  # Reasonable BTC price as of May 2025
            return recent_avg, recent_avg * 0.99, recent_avg * 1.01  # 1% CI
    
    def update(self, new_observation):
        """
        Update the model with a new observation.
        
        Args:
            new_observation: New Bitcoin price observation
        """
        try:
            # Convert to tensor and ensure float64
            new_observation = tf.convert_to_tensor(new_observation, dtype=tf.float64)
            
            # Rebuild the model with the new observation (this is important!)
            # This prevents TF variable sharing issues
            self.build_model(new_observation)
            
            # Get model config from the service-specific section directly
            model_config = None
            
            # Check if service-specific config exists at top level and has model section
            if self.service_name in self.config and 'model' in self.config[self.service_name]:
                model_config = self.config[self.service_name]['model']['instant']
            else:
                # Fallback to global model config if service-specific not found
                model_config = self.config.get('model', {}).get('instant', {})
            
            # If we still don't have a valid config, use defaults
            if not model_config:
                model_config = {}
            
            # Fit with the new model and a new optimizer
            self.fit(new_observation, num_variational_steps=model_config.get('vi_steps', 10))
            
        except Exception as e:
            print(f"Error updating model: {e}\n{traceback.format_exc()}")
            # Don't raise, allow the app to continue with fallback predictions 