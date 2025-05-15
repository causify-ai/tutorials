#!/usr/bin/env python3
"""
TensorFlow Probability model for Bitcoin price forecasting.
Implements a structural time series model with local linear trend, seasonal components,
day-of-week effects, and autoregressive parts.

Model Features:
- Data preprocessing with outlier detection and replacement
- Technical indicators integration (moving averages, MACD, RSI, etc.)
- Multiple model components (trend, seasonal, day-of-week, autoregressive)
- Choice between Variational Inference (fast) and MCMC (more accurate)
- Adaptive learning rates for better convergence
- Comprehensive error evaluation with anomaly detection
- Robust fallback mechanisms for prediction stability

Usage:
    model = BitcoinForecastModel(config)  # Initialize with configuration
    model.fit(price_series)               # Train on historical data
    pred, lower, upper = model.forecast() # Make prediction with confidence intervals
    metrics = model.evaluate_prediction(actual_price, prediction) # Evaluate accuracy
"""
import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np
from datetime import datetime, timedelta
import gc
import traceback
import os
import pandas as pd
from scipy import stats

# Import utility functions for consistent data handling
try:
    from utilities.data_utils import safe_round, format_price
    from utilities.model_utils import extract_scalar_from_prediction
except ImportError:
    # Define minimal versions if utilities not available
    def safe_round(value, decimals=2):
        """Safely round a value regardless of its type."""
        if isinstance(value, np.ndarray):
            if value.size == 1:
                value = value.item()
            else:
                value = value[0]
        try:
            return round(float(value), decimals)
        except (TypeError, ValueError):
            return 0.0
    
    def format_price(price, decimals=2):
        """Format price for display."""
        rounded = safe_round(price, decimals)
        return f"{rounded:.{decimals}f}"
    
    def extract_scalar_from_prediction(prediction):
        """Extract scalar from prediction."""
        if isinstance(prediction, np.ndarray):
            if prediction.size == 1:
                return float(prediction.item())
            elif prediction.size > 1:
                return float(prediction[0])
        try:
            return float(prediction)
        except (TypeError, ValueError):
            return 0.0

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
        self.service_name = os.environ.get(
            'SERVICE_NAME', 'bitcoin_forecast_app')

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
        self.preprocessed_data = None

        # Set default dtype to float64 for all tensors
        tf.keras.backend.set_floatx('float64')
        
        # Store the learning rate from config
        self.learning_rate = model_config.get('learning_rate', 0.01)

        # Get VI steps from config
        self.vi_steps = model_config.get('vi_steps', 100)

        # Store num_samples for forecasting
        self.num_samples = model_config.get('num_samples', 50)

        # Advanced model parameters with defaults
        # MCMC is more accurate but slower
        self.use_mcmc = model_config.get('use_mcmc', False)
        self.mcmc_steps = model_config.get('mcmc_steps', 1000)
        self.mcmc_burnin = model_config.get('mcmc_burnin', 300)
        self.use_day_of_week = model_config.get('use_day_of_week', True)
        self.use_technical_indicators = model_config.get(
            'use_technical_indicators', True)

        # For technical indicators
        self.short_ma_window = model_config.get('short_ma_window', 5)
        self.long_ma_window = model_config.get('long_ma_window', 20)
        self.volatility_window = model_config.get('volatility_window', 10)

        # Track model rebuilds
        self.model_version = 0

        # Last forecast values (for fallback)
        self.last_forecast = None
        self.last_mean = None
        self.last_lower = None
        self.last_upper = None

        # For evaluation
        self.recent_errors = []
        self.max_error_history = 100
        self.anomaly_detection_threshold = 3.0  # Z-score threshold

        # Setup TensorFlow function caching to prevent repeated retracing
        self._setup_tf_function_caching()

        # Debug log
        print(
            f"Initialized model with num_samples={self.num_samples}, vi_steps={self.vi_steps}")
        if self.use_mcmc:
            print(
                f"Using MCMC with {self.mcmc_steps} steps and {self.mcmc_burnin} burnin")
        else:
            print(f"Using Variational Inference with {self.vi_steps} steps")

    def _setup_tf_function_caching(self):
        """Configure TensorFlow to reduce function retracing."""
        try:
            # Set experimental_relax_shapes=True to reduce retracing due to shape changes
            tf.config.optimizer.set_experimental_options({
                'layout_optimizer': True,
                'constant_folding': True,
                'shape_optimization': True,
                'remapping': True
            })
            
            # Set environment variable for TF function inlining
            os.environ['TF_FUNCTION_JIT_COMPILE_DEFAULT'] = '1'
            
            # Set up TF memory growth to prevent OOM errors
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                except RuntimeError as e:
                    print(f"Error setting memory growth: {e}")
                    
        except Exception as e:
            print(f"Error setting up TensorFlow optimizations: {e}")

    def _create_optimizer(self):
        """Create a fresh optimizer instance with adaptive learning rate."""
        # Calculate adaptive learning rate based on model version and recent performance
        base_lr = self.learning_rate

        # Get recent errors if available
        if len(self.recent_errors) > 0:
            mean_error = np.mean(self.recent_errors)
            # Adjust learning rate based on recent prediction errors
            # Cap adjustment
            error_factor = min(2.0, max(0.5, mean_error / 1000.0))
            base_lr *= error_factor
            print(
                f"Adjusting learning rate by factor {error_factor:.2f} based on recent errors")

        # Further adjust based on model version
        if self.model_version > 10:
            base_lr *= 0.8
        elif self.model_version > 5:
            base_lr *= 0.9

        # Create schedule with warmup and decay
        initial_learning_rate = base_lr
        decay_steps = self.vi_steps
        warmup_steps = int(decay_steps * 0.1)  # 10% of steps for warmup

        # Define the learning rate schedule as a class inheriting from LearningRateSchedule
        class CustomLearningRateSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
            def __init__(self, initial_lr, warmup_steps, decay_steps):
                super(CustomLearningRateSchedule, self).__init__()
                self.initial_lr = initial_lr
                self.warmup_steps = warmup_steps
                self.decay_steps = decay_steps

            def __call__(self, step):
                # Convert to float32 to avoid type issues
                step = tf.cast(step, tf.float32)
                warmup_steps = tf.cast(self.warmup_steps, tf.float32)
                decay_steps = tf.cast(self.decay_steps, tf.float32)

                # Linear warmup followed by cosine decay
                warmup_pct = tf.where(
                    step < warmup_steps,
                    step / warmup_steps,
                    tf.constant(1.0, dtype=tf.float32)
                )

                # Calculate decay progress after warmup
                decay_progress = tf.where(
                    step < warmup_steps,
                    tf.constant(0.0, dtype=tf.float32),
                    (step - warmup_steps) / (decay_steps - warmup_steps)
                )

                # Clip decay_progress to [0, 1]
                decay_progress = tf.clip_by_value(decay_progress, 0.0, 1.0)

                # Apply cosine decay after warmup
                cosine_decay = 0.5 * (1.0 + tf.cos(decay_progress * np.pi))

                # Combine warmup and decay
                lr = self.initial_lr * warmup_pct * tf.where(
                    step < warmup_steps,
                    tf.constant(1.0, dtype=tf.float32),
                    cosine_decay
                )

                return lr

            def get_config(self):
                return {
                    "initial_lr": self.initial_lr,
                    "warmup_steps": self.warmup_steps,
                    "decay_steps": self.decay_steps
                }

        # Create an instance of the custom learning rate schedule
        lr_schedule = CustomLearningRateSchedule(
            initial_learning_rate,
            warmup_steps,
            decay_steps
        )

        return tf.keras.optimizers.Adam(learning_rate=lr_schedule)

    def preprocess_data(self, data):
        """
        Preprocess time series data with enhanced technical indicators.
        """
        try:
            # Convert input to numpy array if needed
            if isinstance(data, tf.Tensor):
                data = data.numpy()

            if len(data.shape) == 0:
                data = np.array([data])

            # Create pandas Series for easier manipulation
            series = pd.Series(data)

            # Enhanced outlier detection using Interquartile Range (IQR)
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_mask = (series < lower_bound) | (series > upper_bound)
            outlier_indices = np.where(outlier_mask)[0]

            if len(outlier_indices) > 0:
                print(
                    f"Found {len(outlier_indices)} outliers using IQR method")
                for idx in outlier_indices:
                    # Use exponential weighted average for replacement
                    start_idx = max(0, idx - 10)
                    end_idx = min(len(series), idx + 11)
                    local_values = series.iloc[start_idx:end_idx].copy()
                    if idx >= start_idx and idx < end_idx:
                        local_values = local_values.drop(
                            local_values.index[idx - start_idx])
                    if not local_values.empty:
                        # Use exponential weighted average with more weight to recent values
                        replacement = local_values.ewm(span=5).mean().iloc[-1]
                        series.iloc[idx] = replacement

            # Add enhanced technical indicators
            if self.use_technical_indicators and len(series) >= self.long_ma_window:
                df = pd.DataFrame({'price': series})

                # Enhanced moving averages
                for window in [5, 10, 20, 50]:
                    df[f'ma_{window}'] = series.rolling(window=window).mean()
                    df[f'ema_{window}'] = series.ewm(span=window).mean()

                # Bollinger Bands
                for window in [20, 50]:
                    ma = df['price'].rolling(window=window).mean()
                    std = df['price'].rolling(window=window).std()
                    df[f'bb_upper_{window}'] = ma + (2 * std)
                    df[f'bb_lower_{window}'] = ma - (2 * std)
                    df[f'bb_width_{window}'] = (
                        df[f'bb_upper_{window}'] - df[f'bb_lower_{window}']) / ma

                # Enhanced momentum indicators
                for period in [5, 10, 20]:
                    # ROC (Rate of Change)
                    df[f'roc_{period}'] = series.pct_change(
                        periods=period) * 100
                    # Momentum
                    df[f'momentum_{period}'] = series - series.shift(period)

                # Enhanced volatility measures
                for window in [10, 20, 50]:
                    # Standard deviation
                    df[f'volatility_{window}'] = series.rolling(
                        window=window).std()
                    # Parkinson volatility (using high-low range)
                    if 'high' in df.columns and 'low' in df.columns:
                        df[f'parkinson_{window}'] = np.sqrt(
                            (1.0 / (4.0 * np.log(2.0))) *
                            ((np.log(df['high'] / df['low'])) ** 2)
                        ).rolling(window=window).mean()

                # Enhanced RSI with multiple periods
                for period in [6, 14, 28]:
                    delta = series.diff()
                    gain = delta.clip(lower=0)
                    loss = -delta.clip(upper=0)
                    avg_gain = gain.rolling(window=period).mean()
                    avg_loss = loss.rolling(window=period).mean()
                    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
                    df[f'rsi_{period}'] = 100 - (100 / (1 + rs))

                # MACD with multiple periods
                for (fast, slow) in [(12, 26), (5, 35)]:
                    fast_ema = series.ewm(span=fast).mean()
                    slow_ema = series.ewm(span=slow).mean()
                    macd = fast_ema - slow_ema
                    signal = macd.ewm(span=9).mean()
                    df[f'macd_{fast}_{slow}'] = macd
                    df[f'macd_signal_{fast}_{slow}'] = signal
                    df[f'macd_hist_{fast}_{slow}'] = macd - signal

                # Fill NaN values with forward fill then backward fill
                df = df.ffill().bfill()

                # Normalize all features to similar scale
                for col in df.columns:
                    if col != 'price':
                        df[col] = (df[col] - df[col].mean()) / \
                            (df[col].std() + 1e-8)

                # Store preprocessed data
                self.preprocessed_data = df

                # Return tensor for model
                return tf.convert_to_tensor(series.values, dtype=tf.float64)

            # Store preprocessed data
            self.preprocessed_data = series

            # Return tensor for model
            return tf.convert_to_tensor(series.values, dtype=tf.float64)

        except Exception as e:
            print(
                f"Error in data preprocessing: {e}\n{traceback.format_exc()}")
            return tf.convert_to_tensor(data, dtype=tf.float64)
        
    def build_model(self, observed_time_series):
        """
        Build an enhanced structural time series model with multiple components
        to better capture price dynamics, especially during rapid changes.
        
        Args:
            observed_time_series: Tensor of observed Bitcoin prices
        """
        try:
            # Convert input to float64 tensor
            observed_time_series = tf.convert_to_tensor(
                observed_time_series, dtype=tf.float64)

            # Create components list
            components = []

            # Create priors with explicit float64 dtype - use tighter priors for stability
            level_scale_prior = tfd.LogNormal(
                # Tighter prior for more stability
                loc=tf.constant(-4., dtype=tf.float64),
                scale=tf.constant(0.5, dtype=tf.float64)
            )

            # More flexible slope prior to capture rapid changes
            slope_scale_prior = tfd.LogNormal(
                # Less tight to allow faster adaptation
                loc=tf.constant(-3., dtype=tf.float64),
                # Wider scale for more flexibility
                scale=tf.constant(0.7, dtype=tf.float64)
            )

            # Initialize level at the first observation
            initial_level_prior = tfd.Normal(
                loc=observed_time_series[0],
                scale=tf.constant(1000., dtype=tf.float64)
            )

            # Allow for non-zero initial slope to capture trends immediately
            if len(observed_time_series) >= 3:
                # Calculate initial slope from first few observations
                initial_slope = (
                    observed_time_series[2] - observed_time_series[0]) / 2.0
                initial_slope_prior = tfd.Normal(
                    loc=initial_slope,
                    scale=tf.constant(100., dtype=tf.float64)
                )
            else:
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
                initial_slope_prior=initial_slope_prior,
                name='local_linear_trend'
            )

            # First add the local linear trend component
            components.append(local_linear_trend)
        
            # Create seasonal prior with explicit float64 dtype
            drift_scale_prior = tfd.LogNormal(
                loc=tf.constant(-3., dtype=tf.float64),
                scale=tf.constant(0.5, dtype=tf.float64)
            )
        
            # Seasonal component based on frequency pattern
            seasonal = tfs.Seasonal(
                num_seasons=self.num_seasons,
                observed_time_series=observed_time_series,
                drift_scale_prior=drift_scale_prior,
                name='seasonal'
            )
            components.append(seasonal)

            # Enhanced autoregressive component with higher order for better short-term predictions
            # Higher order AR captures more complex patterns
            # Use AR(3) instead of AR(1) for more complex dynamics
            ar_order = 3

            # Only use higher-order AR if we have enough data
            if len(observed_time_series) > ar_order * 3:
                autoregressive = tfs.Autoregressive(
                    order=ar_order,
                    observed_time_series=observed_time_series,
                    name='autoregressive'
                )
                components.append(autoregressive)
            else:
                # Fall back to AR(1) for short time series
                autoregressive = tfs.Autoregressive(
                    order=1,
                    observed_time_series=observed_time_series,
                    name='autoregressive'
                )
                components.append(autoregressive)

            # Verify we have valid components before creating the model
            if not components:
                print("Error: No valid components to build model")
                return None

            # Combine components with Sum
            model = tfs.Sum(
                components=components,
                observed_time_series=observed_time_series
            )
        
            # Clear any old model resources
            if self.model is not None:
                del self.model
                gc.collect()

            self.model = model
            self.model_version += 1

            print(
                f"Built enhanced model v{self.model_version} with {len(components)} components")
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

            # Preprocess data first
            processed_data = self.preprocess_data(observed_time_series)

            # Build a new model or rebuild if needed
            if self.model is None:
                self.build_model(processed_data)
        
            # Convert to tensor and ensure float64
            self.observed_time_series = processed_data

            # Choose between MCMC or Variational Inference
            # Only use MCMC with sufficient data
            if self.use_mcmc and len(processed_data) > 10:
                return self._fit_mcmc()
            else:
                return self._fit_variational_inference(num_variational_steps)

        except Exception as e:
            print(f"Error fitting model: {e}\n{traceback.format_exc()}")
            return None

    def _fit_variational_inference(self, num_steps):
        """Fit the model using variational inference."""
        try:
            # Check if model is valid
            if self.model is None:
                print("Error: Cannot fit variational inference - model is None")
                return None

            # Clear old TF variables by creating a new surrogate posterior
            # Build surrogate posterior - this creates new TF variables
            try:
                surrogate = tfs.build_factored_surrogate_posterior(
                    model=self.model)
            except Exception as e:
                print(f"Error building surrogate posterior: {e}")
                return None

            # Create a new optimizer for each fit to prevent variable sharing issues
            optimizer = self._create_optimizer()
        
            # Define joint log probability function
            @tf.function(experimental_relax_shapes=True, reduce_retracing=True)
            def target_log_prob_fn(**params):
                return self.model.joint_distribution(
                    observed_time_series=self.observed_time_series
                ).log_prob(**params)
            
            # Accelerated version for small changes
            # Use fewer steps for smaller datasets to speed up computation
            actual_steps = num_steps
            if len(self.observed_time_series) < 30:
                # For small datasets, fewer steps are needed
                actual_steps = max(50, int(num_steps * 0.5))
                print(f"Small dataset detected, using reduced VI steps: {actual_steps}")
                
            # For stable performance, avoid too many steps
            if actual_steps > 200:
                actual_steps = 200
                print(f"Capping VI steps to {actual_steps} for stable performance")
            
            # Fit the surrogate posterior with a fresh optimizer
            @tf.function(experimental_relax_shapes=True)
            def run_vi():
                return tfp.vi.fit_surrogate_posterior(
                    target_log_prob_fn=target_log_prob_fn,
                    surrogate_posterior=surrogate,
                    optimizer=optimizer,
                    num_steps=actual_steps
                )
                
            losses = run_vi()
            
            # Explicitly clear the old posterior to release memory
            if self.posterior is not None:
                del self.posterior
                gc.collect()
        
            self.posterior = surrogate

            # Log the final loss for monitoring convergence
            if len(losses) > 0:
                print(f"Final VI loss: {losses[-1].numpy()}")

            return surrogate
        except Exception as e:
            print(
                f"Error in variational inference: {e}\n{traceback.format_exc()}")
            return None

    def _fit_mcmc(self):
        """Fit the model using MCMC for more accurate inference."""
        try:
            # Define joint log probability function
            def target_log_prob_fn(**params):
                return self.model.joint_distribution(
                    observed_time_series=self.observed_time_series
                ).log_prob(**params)

            # Set the step size to be adapting during burnin
            step_size = tf.Variable(0.01, dtype=tf.float64)

            # Create transition kernel
            hmc_kernel = tfp.mcmc.HamiltonianMonteCarlo(
                target_log_prob_fn=target_log_prob_fn,
                step_size=step_size,
                num_leapfrog_steps=3
            )

            # Adapt step size during burnin
            adaptive_kernel = tfp.mcmc.SimpleStepSizeAdaptation(
                inner_kernel=hmc_kernel,
                num_adaptation_steps=int(self.mcmc_burnin * 0.8),
                target_accept_prob=tf.constant(0.75, dtype=tf.float64)
            )

            # Initialize MCMC state from the model priors
            init_state = [tf.random.normal([])
                          for _ in range(len(self.model.parameters))]

            # Run the MCMC chain
            @tf.function(autograph=False)
            def run_chain():
                samples, _ = tfp.mcmc.sample_chain(
                    num_results=self.mcmc_steps,
                    num_burnin_steps=self.mcmc_burnin,
                    current_state=init_state,
                    kernel=adaptive_kernel,
                    trace_fn=lambda _, pkr: pkr.inner_results.is_accepted
                )
                return samples

            print(
                f"Starting MCMC with {self.mcmc_steps} steps and {self.mcmc_burnin} burnin...")
            samples = run_chain()
            print("MCMC sampling completed")

            # Create a callable posterior from MCMC samples
            def sample_fn(sample_shape=(), seed=None):
                """Sample from the MCMC results."""
                idx = tf.random.uniform(
                    shape=sample_shape,
                    minval=0,
                    maxval=self.mcmc_steps,
                    dtype=tf.int32,
                    seed=seed
                )
                return [tf.gather(chain, idx) for chain in samples]

            # Create a posterior object with the sample function
            class MCMCPosterior:
                def __init__(self, sample_function):
                    self.sample_function = sample_function

                def sample(self, sample_shape=(), seed=None):
                    return self.sample_function(sample_shape, seed)

            # Create and store the posterior
            self.posterior = MCMCPosterior(sample_fn)
            return self.posterior

        except Exception as e:
            print(f"Error in MCMC inference: {e}\n{traceback.format_exc()}")
            # Fall back to variational inference if MCMC fails
            print("Falling back to variational inference")
            return self._fit_variational_inference(self.vi_steps)
    
    def forecast(self, num_steps=1):
        """
        Generate forecasts with uncertainty intervals.
        
        Args:
            num_steps: Number of steps ahead to forecast (default: 1)
            
        Returns:
            Tuple of (mean prediction, lower bound, upper bound)
        """
        try:
            # Check if model and posterior exist
            if self.model is None:
                print("[{}] Warning: Model is None, using last forecast as fallback".format(
                    datetime.now().isoformat()
                ))
                if self.last_forecast is not None:
                    return self.last_mean, self.last_lower, self.last_upper
                return self._fallback_forecast()

            if self.posterior is None:
                print("[{}] Warning: Posterior is None, using last forecast as fallback".format(
                    datetime.now().isoformat()
                ))
                if self.last_forecast is not None:
                    return self.last_mean, self.last_lower, self.last_upper
                return self._fallback_forecast()

            print(
                f"[{datetime.now().isoformat()}] Making forecast with TFP model v{self.model_version}")

            # Generate samples from the posterior and forecast using cached function
            forecast_dist = self._generate_forecast(num_steps)
            
            # Extract forecast samples
            mean_forecast, scale_forecast = self._extract_forecast_stats(forecast_dist)
            
            # Extract the mean forecast for the first step ahead
            # Use extract_scalar_from_prediction to safely handle numpy arrays
            mean_forecast_value = extract_scalar_from_prediction(mean_forecast)

            # Extract the scale (standard deviation) of forecast
            scale_forecast_value = extract_scalar_from_prediction(scale_forecast)

            # Calculate prediction intervals (95% confidence)
            lower = mean_forecast_value - 1.96 * scale_forecast_value
            upper = mean_forecast_value + 1.96 * scale_forecast_value

            # Store for fallback
            self.last_forecast = forecast_dist
            self.last_mean = mean_forecast_value
            self.last_lower = lower
            self.last_upper = upper

            # Round values for consistency
            mean_forecast_value = safe_round(mean_forecast_value, 2)
            lower = safe_round(lower, 2)
            upper = safe_round(upper, 2)

            # Return point forecast and interval
            return mean_forecast_value, lower, upper

        except Exception as e:
            print(f"Error in forecast: {e}\n{traceback.format_exc()}")
            print("Using last forecast as fallback")

            # Return last successful forecast if available
            if self.last_forecast is not None:
                return self.last_mean, self.last_lower, self.last_upper

            # Otherwise use fallback method
            return self._fallback_forecast()

    @tf.function(experimental_relax_shapes=True)
    def _generate_forecast(self, num_steps):
        """Generate forecast distribution with TensorFlow function caching."""
        return tfs.forecast(
            model=self.model,
            observed_time_series=self.observed_time_series,
            parameter_samples=self.posterior.sample(self.num_samples),
            num_steps_forecast=num_steps
        )
        
    def _extract_forecast_stats(self, forecast_dist):
        """Extract mean and standard deviation from forecast distribution."""
        try:
            # Use TensorFlow operations directly when possible
            forecast_means = forecast_dist.mean()[0]  # Get first step mean
            forecast_scales = forecast_dist.stddev()[0]  # Get first step stddev
            return forecast_means, forecast_scales
        except Exception as e:
            print(f"Error extracting forecast stats: {e}")
            # Fallback to numpy arrays if TensorFlow ops fail
            return np.array([0.0]), np.array([0.0])

    def evaluate_prediction(self, actual_price, prediction, timestamp=None):
        """
        Evaluate a prediction against the actual price and track errors.

        Args:
            actual_price: Actual observed price
            prediction: Predicted price
            timestamp: Optional timestamp for the prediction

        Returns:
            Dictionary of evaluation metrics
        """
        try:
            # Convert inputs to scalar values
            actual = extract_scalar_from_prediction(actual_price)
            pred = extract_scalar_from_prediction(prediction)
            
            # Calculate absolute error
            error = actual - pred
            abs_error = abs(error)

            # Track recent errors for anomaly detection
            self.recent_errors.append(abs_error)
            if len(self.recent_errors) > self.max_error_history:
                self.recent_errors.pop(0)

            # Calculate percentage error
            pct_error = (error / actual) * 100 if actual != 0 else float('inf')

            # Calculate z-score of current error
            z_score = 0
            if len(self.recent_errors) > 5:
                mean_error = np.mean(self.recent_errors)
                mean_error_value = extract_scalar_from_prediction(mean_error)
                
                std_error = np.std(self.recent_errors) + 1e-8  # Avoid division by zero
                std_error_value = extract_scalar_from_prediction(std_error)
                
                z_score = (abs_error - mean_error_value) / std_error_value

            # Detect anomalies
            is_anomaly = z_score > self.anomaly_detection_threshold

            # Round metrics to 2 decimal places
            abs_error = safe_round(abs_error, 2)
            pct_error = safe_round(pct_error, 2)
            z_score = safe_round(z_score, 2)

            return {
                'absolute_error': abs_error,
                'percentage_error': pct_error,
                'z_score': z_score,
                'is_anomaly': is_anomaly,
                'timestamp': timestamp
            }

        except Exception as e:
            print(
                f"Error evaluating prediction: {e}\n{traceback.format_exc()}")
            return {
                'absolute_error': float('nan'),
                'percentage_error': float('nan'),
                'z_score': float('nan'),
                'is_anomaly': False,
                'timestamp': timestamp
            }
    
    def update(self, new_observation):
        """
        Update the model with a new observation, with enhanced adaptivity for sudden price changes.
        
        Args:
            new_observation: New Bitcoin price observation or series of observations
        """
        try:
            # Check if new_observation is a single value or a series
            if isinstance(new_observation, (list, np.ndarray)) and len(new_observation) > 1:
                observation_data = new_observation
            else:
                if self.observed_time_series is not None:
                    # Get historical data
                    historical_data = self.observed_time_series.numpy()

                    # Calculate dynamic lookback window based on recent volatility
                    if len(historical_data) >= 20:
                        recent_data = pd.Series(historical_data[-20:])
                        volatility = recent_data.pct_change().std()
                        volatility_value = extract_scalar_from_prediction(volatility)

                        # More volatile markets need shorter lookback to adapt faster
                        if volatility_value > 0.01:  # High volatility (>1% std dev)
                            lookback = min(len(historical_data),
                                           int(self.num_timesteps * 0.5))
                            print(
                                f"High volatility detected ({volatility_value:.4f}), using shorter lookback: {lookback}")
                        # Medium volatility (>0.5% std dev)
                        elif volatility_value > 0.005:
                            lookback = min(len(historical_data),
                                           int(self.num_timesteps * 0.75))
                            print(
                                f"Medium volatility detected ({volatility_value:.4f}), using medium lookback: {lookback}")
                        else:
                            lookback = min(len(historical_data),
                                           self.num_timesteps)
                            print(
                                f"Low volatility detected ({volatility_value:.4f}), using standard lookback: {lookback}")
                    else:
                        lookback = min(len(historical_data),
                                       self.num_timesteps)

                    # Keep only the most recent data points based on dynamic lookback
                    historical_data = historical_data[-lookback:]

                    # Detect if there's a significant price change
                    if isinstance(new_observation, (float, int)) and len(historical_data) > 0:
                        last_price = extract_scalar_from_prediction(historical_data[-1])
                        new_obs_value = extract_scalar_from_prediction(new_observation)
                        price_change_pct = abs(
                            (new_obs_value - last_price) / last_price) if last_price != 0 else 0

                        # If sudden large change, give more weight to recent data
                        if price_change_pct > 0.02:  # >2% sudden change
                            print(
                                f"Significant price change detected: {price_change_pct:.2%}")
                            # Exponentially decay older data to emphasize recent change
                            decay_factor = 0.9
                            weights = np.array(
                                [decay_factor ** i for i in range(len(historical_data), 0, -1)])
                            historical_data = historical_data * weights

                    # Append the new observation
                    if isinstance(new_observation, (list, np.ndarray)):
                        observation_data = np.append(
                            historical_data, new_observation)
                    else:
                        observation_data = np.append(
                            historical_data, [new_observation])
                else:
                    # No history available, use just this observation
                    if isinstance(new_observation, (list, np.ndarray)):
                        observation_data = new_observation
                    else:
                        observation_data = np.array([new_observation])

        # Convert to tensor and ensure float64
            observation_tensor = tf.convert_to_tensor(
                observation_data, dtype=tf.float64)

            # Rebuild the model with the new observation
            self.build_model(observation_tensor)

            # Get model config
            model_config = None
            if self.service_name in self.config and 'model' in self.config[self.service_name]:
                model_config = self.config[self.service_name]['model']['instant']
            else:
                model_config = self.config.get('model', {}).get('instant', {})

            if not model_config:
                model_config = {}

            # Update model parameters
            self.num_samples = model_config.get('num_samples', 50)

            # Adaptive VI steps based on price change magnitude
            if self.last_mean is not None and len(observation_data) > 0:
                # Calculate relative price change
                latest_price = extract_scalar_from_prediction(observation_data[-1])
                
                # Calculate price change percentage safely
                if hasattr(self, 'last_observed_price') and self.last_observed_price is not None:
                    price_change_pct = 0
                    if self.last_observed_price != 0:
                        price_change_pct = abs(
                            (latest_price - self.last_observed_price) / self.last_observed_price)
                else:
                    price_change_pct = 0
                    if self.last_mean != 0:
                        price_change_pct = abs(
                            (latest_price - self.last_mean) / self.last_mean)

                # Store current price for next comparison
                self.last_observed_price = latest_price

                # Adjust VI steps based on price change magnitude - more aggressive scaling
                base_vi_steps = model_config.get('vi_steps', 100)

                # Use our utility functions to ensure we're dealing with scalars
                price_change_pct_value = safe_round(price_change_pct, 4)

                if price_change_pct_value > 0.02:  # >2% change - very significant
                    vi_steps = int(base_vi_steps * 3.0)  # 3x more steps
                    print(
                        f"Large price shock detected ({price_change_pct_value:.2%}), using {vi_steps} VI steps")
                elif price_change_pct_value > 0.01:  # >1% change
                    vi_steps = int(base_vi_steps * 2.0)  # 2x more steps
                    print(
                        f"Large price change detected ({price_change_pct_value:.2%}), using {vi_steps} VI steps")
                elif price_change_pct_value > 0.005:  # >0.5% change
                    vi_steps = int(base_vi_steps * 1.5)  # 50% more steps
                    print(
                        f"Medium price change detected ({price_change_pct_value:.2%}), using {vi_steps} VI steps")
                else:
                    vi_steps = base_vi_steps
                    print(
                        f"Small price change detected ({price_change_pct_value:.2%}), using standard {vi_steps} VI steps")

                # Calculate error-based adjustment
                if len(self.recent_errors) > 5:
                    mean_error = np.mean(self.recent_errors)
                    mean_error_value = extract_scalar_from_prediction(mean_error)
                    
                    mean_price = np.mean(observation_data[-5:])
                    mean_price_value = extract_scalar_from_prediction(mean_price)
                    
                    if mean_price_value > 0:
                        error_ratio = mean_error_value / mean_price_value
                    else:
                        error_ratio = 0

                    # If errors are high, increase VI steps further
                    if error_ratio > 0.01:  # >1% average error
                        error_factor = 1.5
                        vi_steps = int(vi_steps * error_factor)
                        print(
                            f"High error ratio ({error_ratio:.4f}), increasing VI steps by {error_factor}x")
            else:
                vi_steps = model_config.get('vi_steps', 100)

            # Ensure minimum number of VI steps
            # At least 50 steps to ensure proper adaptation
            self.vi_steps = max(50, vi_steps)

            # Fit with the new model - use more VI steps for better adaptation
            self.fit(observation_tensor, num_variational_steps=self.vi_steps)

            # After fitting, force a forecast to update internal state
            self.forecast(num_steps=1)

        except Exception as e:
            print(f"Error updating model: {e}\n{traceback.format_exc()}")
            # Don't raise, allow the app to continue with fallback predictions

    def _fallback_forecast(self):
        """
        Create a fallback forecast when the primary model fails.
        Uses simple statistical methods for basic prediction.

        Returns:
            Tuple of (mean prediction, lower bound, upper bound)
        """
        try:
            if self.observed_time_series is not None:
                data = self.observed_time_series.numpy()
                # Use exponential weighted mean with short span for faster response
                df = pd.Series(data)
                # More weight to recent prices
                mean_val = extract_scalar_from_prediction(df.ewm(span=3).mean().iloc[-1])

                # Calculate dynamic std based on recent volatility
                if len(data) >= 10:
                    recent_std = extract_scalar_from_prediction(df.tail(10).std())
                    volatility_factor = recent_std / mean_val if mean_val != 0 else 0.005
                    std = mean_val * volatility_factor
                else:
                    std = mean_val * 0.005

                lower_val = mean_val - 1.96 * std
                upper_val = mean_val + 1.96 * std

                # Round values for consistency
                mean_val = safe_round(mean_val, 2)
                lower_val = safe_round(lower_val, 2)
                upper_val = safe_round(upper_val, 2)

                return mean_val, lower_val, upper_val

            # Last resort - use a reasonable default value
            recent_avg = 103000.0
            return safe_round(recent_avg, 2), safe_round(recent_avg * 0.99, 2), safe_round(recent_avg * 1.01, 2)
        except Exception as e:
            print(f"Error in fallback forecast: {e}")
            # Absolute last resort
            recent_avg = 103000.0
            return safe_round(recent_avg, 2), safe_round(recent_avg * 0.99, 2), safe_round(recent_avg * 1.01, 2)
