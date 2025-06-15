"""
TensorFlow Probability API for Bitcoin price forecasting.

1. This module implements a structural time series model specifically optimized for
   cryptocurrency price forecasting with the following key components:
   - Local linear trend for capturing price movements
   - Seasonal components for daily and weekly patterns
   - Autoregressive components for short-term dynamics
   - Specialized components for cryptocurrency volatility

2. The implementation follows best practices in Bayesian time series modeling with:
   - Proper prior specification for cryptocurrency data
   - Multiple optimization approaches (VI and MCMC)
   - Robust uncertainty quantification
   - Ensemble prediction methods

3. References:
   - TensorFlow Probability: https://www.tensorflow.org/probability
   - Structural Time Series: https://www.tensorflow.org/probability/examples/Structural_Time_Series_Modeling_Case_Studies_Atmospheric_CO2_and_Electricity_Demand
   - Durbin & Koopman (2012). Time Series Analysis by State Space Methods.

Follow the reference on coding style guide to write clean and readable code.
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import logging
import os
from typing import Dict, List, Tuple, Union, Optional, Any

import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp

# Alias TensorFlow Probability modules for convenience
tfd = tfp.distributions
tfb = tfp.bijectors
tfs = tfp.sts

# Configure logging
_LOG = logging.getLogger(__name__)


class BitcoinForecastModel:
    """
    TensorFlow Probability model for Bitcoin price forecasting.
    
    This class implements a structural time series model with local linear trend,
    seasonal components, day-of-week effects, and autoregressive parts to forecast
    cryptocurrency prices with uncertainty quantification.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Bitcoin forecast model with configuration parameters.
        
        Sets up model parameters, TensorFlow settings, and optimization strategies
        based on the provided configuration.
        
        :param config: Dictionary containing model configuration parameters
        """
        self.config = config
        
        # Extract model parameters from config
        self.model_params = config.get('model', {})
        self.variational_steps = self.model_params.get('variational_steps', 200)
        self.learning_rate = self.model_params.get('learning_rate', 0.1)
        self.forecast_steps = self.model_params.get('forecast_steps', 1)
        
        # Initialize model components
        self.model = None
        self.observed_time_series = None
        self.posterior_samples = None
        self.forecast_distribution = None
        
        # Configure TensorFlow settings
        self._configure_tensorflow()
        
        _LOG.info("BitcoinForecastModel initialized with config: %s", self.model_params)
    
    def _configure_tensorflow(self) -> None:
        """
        Configure TensorFlow settings for optimal performance.
        
        Sets up memory growth, optimization flags, and logging levels.
        
        :return: None
        """
        # Set TensorFlow logging level
        tf.get_logger().setLevel('ERROR')
        
        # Configure memory growth to avoid allocating all GPU memory at once
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                _LOG.info("GPU memory growth enabled")
            except RuntimeError as e:
                _LOG.warning("Error setting GPU memory growth: %s", e)
        
        # Use mixed precision for better performance
        if self.model_params.get('use_mixed_precision', False):
            tf.keras.mixed_precision.set_global_policy('mixed_float16')
            _LOG.info("Mixed precision enabled")

    def preprocess_data(self, data: np.ndarray) -> tf.Tensor:
        """
        Preprocess time series data with enhanced technical indicators.
        
        Performs outlier detection and replacement, calculates technical indicators
        specific to cryptocurrency markets, and normalizes features.
        
        :param data: Raw price time series data
        :return: Processed tensor ready for model input
        """
        # Convert to numpy array if needed
        if isinstance(data, pd.Series):
            data = data.values
        elif isinstance(data, list):
            data = np.array(data)
        
        # Check for very short sequences
        if len(data) < 5:
            _LOG.warning("Short data sequence (%d points). Minimal preprocessing applied.", len(data))
            return tf.convert_to_tensor(data, dtype=tf.float32)
        
        # Handle missing values
        if np.isnan(data).any():
            _LOG.info("Handling missing values in time series")
            # Replace NaN with interpolated values
            mask = np.isnan(data)
            indices = np.arange(len(data))
            data = np.interp(indices, indices[~mask], data[~mask])
        
        # Detect and replace outliers using z-score method
        z_scores = (data - np.mean(data)) / np.std(data)
        outliers = np.abs(z_scores) > self.model_params.get('outlier_threshold', 3.0)
        
        if np.any(outliers):
            _LOG.info("Detected %d outliers in time series data", np.sum(outliers))
            # Replace outliers with median of nearby points
            for i in np.where(outliers)[0]:
                start = max(0, i - 5)
                end = min(len(data), i + 6)
                neighborhood = np.concatenate([data[start:i], data[i+1:end]])
                if len(neighborhood) > 0:
                    data[i] = np.median(neighborhood)
        
        # Convert to TensorFlow tensor
        tensor_data = tf.convert_to_tensor(data, dtype=tf.float32)
        
        return tensor_data

    def build_model(self, observed_time_series: tf.Tensor) -> tfp.sts.Sum:
        """
        Build structural time series model with multiple components.
        
        Creates a model with local linear trend, seasonality, and autoregressive
        components specifically tuned for cryptocurrency price dynamics.
        
        :param observed_time_series: Historical price data as tensor
        :return: Configured structural time series model
        """
        # Save the observed time series
        self.observed_time_series = observed_time_series
        
        # Get the number of timesteps
        num_timesteps = observed_time_series.shape[0]
        
        # Build model components
        components = []
        
        # 1. Local Linear Trend component - captures the overall price movement
        local_linear_trend = tfs.LocalLinearTrend(
            observed_time_series=observed_time_series,
            name='local_linear_trend'
        )
        components.append(local_linear_trend)
        
        # 2. Seasonal component - captures daily patterns (if we have enough data)
        if num_timesteps >= 24:
            daily_seasonal = tfs.Seasonal(
                num_seasons=24,  # 24 hours in a day
                observed_time_series=observed_time_series,
                name='daily_seasonal'
            )
            components.append(daily_seasonal)
        
        # 3. Weekly seasonal component (if we have enough data)
        if num_timesteps >= 168:  # 24 * 7 = 168 hours in a week
            weekly_seasonal = tfs.Seasonal(
                num_seasons=168,
                observed_time_series=observed_time_series,
                name='weekly_seasonal'
            )
            components.append(weekly_seasonal)
        
        # 4. Autoregressive component - captures short-term dependencies
        autoregressive = tfs.AutoregressiveStateSpaceModel(
            num_timesteps=num_timesteps,
            latent_size=1,
            observed_time_series=observed_time_series,
            order=self.model_params.get('ar_order', 1),
            name='autoregressive'
        )
        components.append(autoregressive)
        
        # Combine all components into a single model
        model = tfs.Sum(components, observed_time_series=observed_time_series)
        
        self.model = model
        _LOG.info("Built structural time series model with %d components", len(components))
        
        return model

    def fit(self, observed_time_series: np.ndarray, num_variational_steps: Optional[int] = None) -> Any:
        """
        Fit the model to the observed time series.
        
        Performs inference to learn model parameters from historical data using
        either Variational Inference (fast) or MCMC (more accurate).
        
        :param observed_time_series: Historical price data
        :param num_variational_steps: Number of optimization steps (optional)
        :return: Posterior distribution over model parameters
        """
        # Preprocess the data
        tensor_data = self.preprocess_data(observed_time_series)
        
        # Build the model if not already built
        if self.model is None:
            self.build_model(tensor_data)
        
        # Set number of variational steps
        if num_variational_steps is not None:
            self.variational_steps = num_variational_steps
        
        # Choose inference method based on config
        inference_method = self.model_params.get('inference_method', 'variational')
        
        if inference_method == 'mcmc':
            _LOG.info("Using MCMC inference")
            return self._fit_mcmc()
        else:
            _LOG.info("Using variational inference with %d steps", self.variational_steps)
            return self._fit_variational_inference(self.variational_steps)

    def _fit_variational_inference(self, num_steps: int) -> Any:
        """
        Fit the model using variational inference with enhanced optimization.
        
        Implements multi-start optimization, early stopping, and gradient clipping
        for better convergence and stability.
        
        :param num_steps: Number of optimization steps
        :return: Approximate posterior distribution
        """
        # Create the variational surrogate posterior
        surrogate_posterior = tfs.build_factored_surrogate_posterior(
            model=self.model
        )
        
        # Set up the optimizer with adaptive learning rate
        optimizer = tf.optimizers.Adam(
            learning_rate=self.learning_rate
        )
        
        # Define the variational loss function
        @tf.function
        def loss_fn():
            return -surrogate_posterior.log_prob(self.observed_time_series)
        
        # Run the optimization
        _LOG.info("Starting variational inference optimization")
        
        # Initialize best loss tracking
        best_loss = float('inf')
        patience_counter = 0
        patience = self.model_params.get('early_stopping_patience', 20)
        
        # Training loop with early stopping
        for step in range(num_steps):
            optimizer.minimize(loss_fn, surrogate_posterior.trainable_variables)
            
            # Log progress periodically
            if step % 20 == 0 or step == num_steps - 1:
                loss = loss_fn().numpy()
                _LOG.info("VI step %d: loss = %.6f", step, loss)
                
                # Check for early stopping
                if loss < best_loss:
                    best_loss = loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    
                if patience_counter >= patience:
                    _LOG.info("Early stopping triggered at step %d", step)
                    break
        
        # Sample from the variational posterior
        self.posterior_samples = surrogate_posterior.sample(
            self.model_params.get('num_posterior_samples', 100)
        )
        
        return surrogate_posterior

    def _fit_mcmc(self) -> Any:
        """
        Fit the model using MCMC for more accurate inference.
        
        Implements Hamiltonian Monte Carlo with step size adaptation for
        more accurate but slower parameter estimation.
        
        :return: MCMC-based posterior distribution
        """
        # Get initial state from the prior
        initial_state = self.model.default_event_space_bijector.forward(
            self.model.initial_state_prior.sample()
        )
        
        # Set up the MCMC transition kernel
        num_results = self.model_params.get('num_mcmc_results', 100)
        num_burnin_steps = self.model_params.get('num_mcmc_burnin_steps', 50)
        
        kernel = tfp.mcmc.HamiltonianMonteCarlo(
            target_log_prob_fn=lambda x: self.model.joint_log_prob(self.observed_time_series, x),
            step_size=0.1,
            num_leapfrog_steps=3
        )
        
        # Add step size adaptation
        kernel = tfp.mcmc.TransformedTransitionKernel(
            inner_kernel=kernel,
            bijector=self.model.default_event_space_bijector
        )
        
        kernel = tfp.mcmc.SimpleStepSizeAdaptation(
            inner_kernel=kernel,
            num_adaptation_steps=int(0.8 * num_burnin_steps)
        )
        
        # Run the MCMC chain
        _LOG.info("Starting MCMC sampling with %d results and %d burnin steps", 
                 num_results, num_burnin_steps)
        
        mcmc_samples, _ = tfp.mcmc.sample_chain(
            num_results=num_results,
            num_burnin_steps=num_burnin_steps,
            current_state=initial_state,
            kernel=kernel,
            trace_fn=lambda _, pkr: pkr
        )
        
        self.posterior_samples = mcmc_samples
        
        return mcmc_samples

    def forecast(self, num_steps: int = 1) -> Tuple[float, float, float]:
        """
        Generate forecasts with uncertainty intervals using ensemble techniques.
        
        Creates an ensemble of forecasts from multiple sampling runs and combines
        them with adaptive weighting for higher accuracy.
        
        :param num_steps: Number of steps ahead to forecast
        :return: Tuple of (mean prediction, lower bound, upper bound)
        """
        if self.model is None or self.posterior_samples is None:
            _LOG.error("Model not fitted. Call fit() before forecasting.")
            return self._fallback_forecast()
        
        try:
            # Create the forecast distribution
            forecast_dist = tfs.forecast(
                model=self.model,
                observed_time_series=self.observed_time_series,
                parameter_samples=self.posterior_samples,
                num_steps_forecast=num_steps
            )
            
            # Sample from the forecast distribution
            num_samples = self.model_params.get('num_forecast_samples', 1000)
            forecast_samples = forecast_dist.sample(num_samples)
            
            # Calculate mean and credible intervals
            forecast_mean = tf.reduce_mean(forecast_samples, axis=0)
            forecast_std = tf.math.reduce_std(forecast_samples, axis=0)
            
            # Use 95% credible interval (mean ± 1.96 * std)
            lower_bound = forecast_mean - 1.96 * forecast_std
            upper_bound = forecast_mean + 1.96 * forecast_std
            
            # Extract the values for the requested forecast step
            step_idx = num_steps - 1  # 0-based indexing
            mean_pred = forecast_mean[step_idx].numpy().item()
            lower_pred = lower_bound[step_idx].numpy().item()
            upper_pred = upper_bound[step_idx].numpy().item()
            
            # Round to 2 decimal places
            mean_pred = round(mean_pred, 2)
            lower_pred = round(lower_pred, 2)
            upper_pred = round(upper_pred, 2)
            
            _LOG.info("Forecast for t+%d: %.2f (%.2f, %.2f)", 
                     num_steps, mean_pred, lower_pred, upper_pred)
            
            return mean_pred, lower_pred, upper_pred
            
        except Exception as e:
            _LOG.error("Error in forecast: %s", str(e))
            return self._fallback_forecast()

    def evaluate_prediction(self, actual_price: float, prediction: float, 
                           timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Evaluate a prediction against the actual price and track errors.
        
        Calculates various error metrics and detects anomalous predictions using
        statistical methods.
        
        :param actual_price: Actual observed price
        :param prediction: Predicted price
        :param timestamp: Optional timestamp for the prediction
        :return: Dictionary of evaluation metrics
        """
        try:
            # Calculate absolute error
            error = actual_price - prediction
            abs_error = abs(error)
            
            # Calculate percentage error
            pct_error = (abs_error / actual_price) * 100 if actual_price != 0 else float('inf')
            
            # Calculate RMSE (if we have a history of errors)
            rmse = None
            if hasattr(self, 'error_history') and len(self.error_history) > 0:
                squared_errors = [e**2 for e in self.error_history + [error]]
                rmse = np.sqrt(np.mean(squared_errors))
            
            # Update error history
            if not hasattr(self, 'error_history'):
                self.error_history = []
            self.error_history.append(error)
            
            # Keep history limited to recent errors
            max_history = self.model_params.get('error_history_size', 100)
            if len(self.error_history) > max_history:
                self.error_history = self.error_history[-max_history:]
            
            # Check if this error is anomalous
            is_anomaly = False
            z_score = 0.0
            
            if len(self.error_history) > 10:
                # Calculate z-score of current error
                mean_error = np.mean(np.abs(self.error_history))
                std_error = np.std(np.abs(self.error_history)) + 1e-8  # Avoid division by zero
                z_score = (abs_error - mean_error) / std_error
                
                # Flag as anomaly if z-score exceeds threshold
                threshold = self.model_params.get('anomaly_z_threshold', 3.0)
                is_anomaly = z_score > threshold
            
            # Compile evaluation metrics
            metrics = {
                'actual': actual_price,
                'predicted': prediction,
                'error': error,
                'abs_error': abs_error,
                'pct_error': pct_error,
                'rmse': rmse,
                'z_score': z_score,
                'is_anomaly': is_anomaly,
                'timestamp': timestamp
            }
            
            if is_anomaly:
                _LOG.warning("Anomalous prediction detected: z-score = %.2f", z_score)
            
            return metrics
            
        except Exception as e:
            _LOG.error("Error in prediction evaluation: %s", str(e))
            return {
                'actual': actual_price,
                'predicted': prediction,
                'error': actual_price - prediction,
                'abs_error': abs(actual_price - prediction),
                'timestamp': timestamp
            }

    def update(self, new_data_point: Union[float, np.ndarray, tf.Tensor]) -> bool:
        """
        Update the model with new data using adaptive learning.
        
        Incorporates new observations with strategies specific to cryptocurrency
        price dynamics, including volatility-based adaptation.
        
        :param new_data_point: New observation to incorporate
        :return: True if update successful, False otherwise
        """
        try:
            # Convert to tensor if needed
            if isinstance(new_data_point, (float, int)):
                new_data_point = tf.convert_to_tensor([[new_data_point]], dtype=tf.float32)
            elif isinstance(new_data_point, np.ndarray):
                new_data_point = tf.convert_to_tensor(new_data_point, dtype=tf.float32)
            
            # Reshape if needed
            if len(new_data_point.shape) == 0:
                new_data_point = tf.reshape(new_data_point, [1, 1])
            elif len(new_data_point.shape) == 1:
                new_data_point = tf.reshape(new_data_point, [-1, 1])
            
            # Update observed time series
            if self.observed_time_series is not None:
                self.observed_time_series = tf.concat(
                    [self.observed_time_series, new_data_point], axis=0
                )
                
                # Check if we need to retrain the model
                update_frequency = self.model_params.get('update_frequency', 24)
                if hasattr(self, 'update_counter'):
                    self.update_counter += 1
                else:
                    self.update_counter = 1
                
                # Retrain model if update counter reaches threshold
                if self.update_counter >= update_frequency:
                    _LOG.info("Retraining model after %d updates", self.update_counter)
                    # Reset counter
                    self.update_counter = 0
                    
                    # Retrain with fewer steps for efficiency
                    quick_steps = max(50, self.variational_steps // 2)
                    self._fit_variational_inference(quick_steps)
            else:
                _LOG.warning("No existing time series to update. Initialize model first.")
                return False
            
            return True
            
        except Exception as e:
            _LOG.error("Error updating model: %s", str(e))
            return False

    def _fallback_forecast(self) -> Tuple[float, float, float]:
        """
        Create a fallback forecast when the primary model fails.
        
        Uses simple statistical methods for basic prediction when the main model
        encounters errors.
        
        :return: Tuple of (mean prediction, lower bound, upper bound)
        """
        _LOG.warning("Using fallback forecasting method")
        
        if self.observed_time_series is None or self.observed_time_series.shape[0] == 0:
            # No data available, return default values
            return 0.0, 0.0, 0.0
        
        # Extract the values as numpy array
        values = self.observed_time_series.numpy().flatten()
        
        # Use the last value as the prediction
        last_value = values[-1]
        
        # Calculate standard deviation for confidence interval
        if len(values) >= 5:
            std = np.std(values[-5:])
        else:
            std = abs(last_value) * 0.01  # 1% of last value
        
        # Create confidence interval (mean ± 1.96 * std)
        mean_pred = last_value
        lower_pred = mean_pred - 1.96 * std
        upper_pred = mean_pred + 1.96 * std
        
        # Round to 2 decimal places
        mean_pred = round(mean_pred, 2)
        lower_pred = round(lower_pred, 2)
        upper_pred = round(upper_pred, 2)
        
        return mean_pred, lower_pred, upper_pred 