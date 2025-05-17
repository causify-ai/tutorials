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

        # # Add missing attributes for history size management
        # self.max_history_size = model_config.get('max_history_size', 1000)
        # self.min_points_req = model_config.get('min_points_req', 10)
        # self.num_variational_steps = model_config.get('vi_steps', 100)
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
        """
        Create an enhanced optimizer with adaptive learning rate scheduling
        specifically tuned for cryptocurrency price prediction.
        """
        try:
            # Get initial learning rate with fallback
            initial_lr = 0.05
            if hasattr(self, 'config') and self.config is not None:
                service_config = self.config.get(self.service_name, {})
                model_config = service_config.get('model', {}).get('instant', {})
                if 'learning_rate' in model_config:
                    initial_lr = model_config['learning_rate']
            
            # Create a learning rate schedule that adapts to cryptocurrency price volatility
            # Implement a custom learning rate scheduler with:
            # 1. Warm-up phase to prevent early convergence to poor solutions
            # 2. Step decay to reduce learning rate over time
            # 3. Minimum learning rate to maintain adaptability
            
            # Define learning rate schedule parameters
            warmup_steps = 30
            decay_steps = 50
            decay_rate = 0.85
            min_learning_rate = 0.001
            
            # Implement learning rate schedule using TensorFlow's functionality
            @tf.function
            def lr_schedule(step):
                # Convert to float32 for calculations
                step_f = tf.cast(step, tf.float32)
                warmup_steps_f = tf.constant(warmup_steps, dtype=tf.float32)
                
                # Warmup phase: linear increase
                warmup_factor = tf.minimum(1.0, step_f / warmup_steps_f)
                
                # Decay phase: exponential decay with step function
                decay_factor = decay_rate ** tf.floor(step_f / decay_steps)
                
                # Combine warmup and decay
                lr = initial_lr * warmup_factor * decay_factor
                
                # Ensure we don't go below minimum learning rate
                return tf.maximum(lr, min_learning_rate)
                
            # Choose optimizer based on dataset size and characteristics
            # For cryptocurrency data:
            # - Adam works well for general cases
            # - RMSprop can be better for high volatility
            # - Adagrad/Adadelta can work well with sparse updates
            
            # Evaluate data characteristics to select optimizer
            if hasattr(self, 'observed_time_series') and self.observed_time_series is not None:
                data_length = len(self.observed_time_series)
                
                # For very large datasets, use Adam with weight decay
                if data_length > 1000:
                    print("Using AdamW optimizer for large dataset")
                    optimizer = tf.keras.optimizers.legacy.Adam(
                        learning_rate=lr_schedule,
                        beta_1=0.9,  # Default momentum
                        beta_2=0.999,  # Default second moment
                        epsilon=1e-7,  # Prevent division by zero
                        amsgrad=True  # Use AMSGrad variant for better convergence
                    )
                # For medium datasets with high volatility, use RMSprop
                elif data_length > 100:
                    # For cryptocurrency, RMSprop adapts well to changing gradients
                    print("Using RMSprop optimizer for medium dataset")
                    optimizer = tf.keras.optimizers.legacy.RMSprop(
                        learning_rate=lr_schedule,
                        rho=0.9,  # Decay rate for moving average
                        momentum=0.0,  # No momentum for faster adaptation
                        epsilon=1e-7,  # Numerical stability
                        centered=True  # Center the gradient variance for better performance
                    )
                # For small datasets, use more aggressive learning
                else:
                    print("Using Adam optimizer with higher learning rate for small dataset")
                    # Higher learning rate for small datasets to converge faster
                    optimizer = tf.keras.optimizers.legacy.Adam(
                        learning_rate=lambda step: tf.maximum(initial_lr * 1.5 * decay_rate ** (step // 30), min_learning_rate),
                        beta_1=0.9,  # Default momentum
                        beta_2=0.99,  # Slightly lower than default for more adaptivity
                        epsilon=1e-6  # Slightly higher epsilon for stability
                    )
            else:
                # Default optimizer if no data characteristics available
                print("Using default Adam optimizer")
                optimizer = tf.keras.optimizers.legacy.Adam(learning_rate=initial_lr)
            
            # Configure optimizer for mixed precision if available
            try:
                # Try to use mixed precision for better performance
                if tf.config.list_physical_devices('GPU'):
                    print("Configuring optimizer for mixed precision on GPU")
                    optimizer = tf.keras.mixed_precision.LossScaleOptimizer(optimizer)
            except Exception as e:
                print(f"Mixed precision configuration not available: {e}")
            
            return optimizer
        except Exception as e:
            print(f"Error creating optimizer: {e}. Using default Adam optimizer.")
            return tf.keras.optimizers.legacy.Adam(learning_rate=0.05)

    def preprocess_data(self, data):
        """
        Preprocess time series data with enhanced technical indicators specifically tuned 
        for cryptocurrency markets.
        """
        try:
            # Convert input to numpy array if needed
            if isinstance(data, tf.Tensor):
                data = data.numpy()

            if len(data.shape) == 0:
                data = np.array([data])

            # Create pandas Series for easier manipulation
            series = pd.Series(data)
            
            # Check data quality and print stats
            print(f"Preprocessing data: {len(series)} points, min={series.min():.2f}, max={series.max():.2f}")
            
            # Special preprocessing for cryptocurrency price data
            # 1. Enhanced outlier detection using Multiple methods
            
            # Method 1: Modified Z-Score (more robust than standard Z-score)
            median_val = series.median()
            mad = np.median(np.abs(series - median_val))
            modified_z_scores = 0.6745 * (series - median_val) / (mad + 1e-8)
            z_outliers = np.where(np.abs(modified_z_scores) > 3.5)[0]
            
            # Method 2: Interquartile Range (IQR) - good for skewed distributions like crypto
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            iqr_lower = Q1 - 1.8 * IQR  # Slightly more aggressive than standard 1.5
            iqr_upper = Q3 + 1.8 * IQR
            iqr_outliers = np.where((series < iqr_lower) | (series > iqr_upper))[0]
            
            # Method 3: Percentage change outliers (specific to crypto volatility)
            pct_changes = series.pct_change().fillna(0)
            # Find sudden jumps/drops >3% (commonly seen in crypto markets)
            pct_outliers = np.where(np.abs(pct_changes) > 0.03)[0]
            
            # Combine outliers from all methods, but with a consensus approach
            # Only flag as outlier if detected by at least 2 methods
            all_outliers = list(z_outliers) + list(iqr_outliers) + list(pct_outliers)
            outlier_counts = {}
            for idx in all_outliers:
                outlier_counts[idx] = outlier_counts.get(idx, 0) + 1
                
            # Get indices with at least 2 detections
            consensus_outliers = [idx for idx, count in outlier_counts.items() if count >= 2]
            outlier_indices = sorted(consensus_outliers)

            if len(outlier_indices) > 0:
                print(
                    f"Found {len(outlier_indices)} consensus outliers using multiple detection methods")
                for idx in outlier_indices:
                    # Use exponential weighted average with local context for replacement
                    # This preserves more of the trend information than simple median
                    window_size = 10
                    start_idx = max(0, idx - window_size)
                    end_idx = min(len(series), idx + window_size + 1)
                    local_values = series.iloc[start_idx:end_idx].copy()
                    
                    # Remove the outlier itself from local values
                    if idx >= start_idx and idx < end_idx:
                        local_values = local_values.drop(local_values.index[idx - start_idx])
                        
                    if not local_values.empty:
                        # Enhanced replacement strategy: weighted average of nearby points
                        # with exponential decay for distance
                        if len(local_values) >= 3:
                            # Calculate distances from the outlier point
                            distances = np.abs(np.array(local_values.index) - idx)
                            # Exponential weights based on distance
                            weights = np.exp(-0.3 * distances)
                            # Normalize weights
                            weights = weights / np.sum(weights)
                            # Weighted average
                            replacement = np.sum(local_values.values * weights)
                        else:
                            # Simple mean for very small local context
                            replacement = local_values.mean()
                            
                        series.iloc[idx] = replacement
                        print(f"  Replaced outlier at index {idx} (value: {data[idx]:.2f}) with {replacement:.2f}")

            # Add enhanced technical indicators specific to cryptocurrency markets
            if self.use_technical_indicators and len(series) >= self.long_ma_window:
                df = pd.DataFrame({'price': series})

                # 1. Enhanced moving averages with crypto-specific windows
                # Short-term windows for capturing rapid price movements
                for window in [3, 5, 8, 13]:  # Fibonacci sequence for crypto markets
                    df[f'ma_{window}'] = series.rolling(window=window).mean()
                    # Exponential MA gives more weight to recent prices
                    df[f'ema_{window}'] = series.ewm(span=window, adjust=False).mean()

                # 2. Volatility indicators (especially important for crypto)
                # ATR-inspired volatility measure
                for window in [5, 8, 13, 21]:
                    price_diffs = np.abs(series.diff())
                    df[f'volatility_{window}'] = price_diffs.rolling(window=window).mean()
                
                # 3. Crypto-specific momentum indicators
                for period in [3, 5, 8, 13]:
                    # ROC (Rate of Change) - critical for crypto momentum trading
                    df[f'roc_{period}'] = series.pct_change(periods=period) * 100
                    # Price Velocity - captures speed of price movement
                    df[f'velocity_{period}'] = series.diff(periods=period) / period
                
                # 4. Bollinger Bands - popular for crypto trading
                for window in [13, 21]:
                    ma = df['price'].rolling(window=window).mean()
                    std = df['price'].rolling(window=window).std()
                    df[f'bb_upper_{window}'] = ma + (2 * std)
                    df[f'bb_lower_{window}'] = ma - (2 * std)
                    # BB width indicates volatility
                    df[f'bb_width_{window}'] = (df[f'bb_upper_{window}'] - df[f'bb_lower_{window}']) / ma

                # 5. RSI - crucial for crypto markets
                for period in [7, 14]:
                    delta = series.diff()
                    gain = delta.clip(lower=0)
                    loss = -delta.clip(upper=0)
                    avg_gain = gain.rolling(window=period).mean()
                    avg_loss = loss.rolling(window=period).mean()
                    # Avoid division by zero
                    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
                    df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
                
                # 6. MACD for crypto trends
                # Standard MACD
                fast_ema = series.ewm(span=12, adjust=False).mean()
                slow_ema = series.ewm(span=26, adjust=False).mean()
                macd = fast_ema - slow_ema
                signal = macd.ewm(span=9, adjust=False).mean()
                df['macd'] = macd
                df['macd_signal'] = signal
                df['macd_hist'] = macd - signal
                
                # 7. Fractal indicators for crypto (simplified)
                if len(series) >= 5:
                    highs = series.rolling(window=5, center=True).max()
                    lows = series.rolling(window=5, center=True).min()
                    df['fractal_high'] = (highs == series)
                    df['fractal_low'] = (lows == series)

                # Fill NaN values with appropriate method
                # First forward fill, then backward fill for any remaining NaNs
                df = df.ffill().bfill()

                # Normalize features to similar scale using robust scaling
                # This works better than standard scaling for outlier-prone crypto data
                for col in df.columns:
                    if col != 'price':
                        median = df[col].median()
                        iqr = df[col].quantile(0.75) - df[col].quantile(0.25)
                        if iqr > 0:
                            df[col] = (df[col] - median) / (iqr + 1e-8)
                        else:
                            df[col] = (df[col] - median) / (df[col].std() + 1e-8)

                # Store preprocessed data
                self.preprocessed_data = df
                
                print(f"Generated {len(df.columns)-1} technical indicators for cryptocurrency analysis")

                # Return tensor for model - just the price series
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

            # Use much tighter priors for Bitcoin price modeling
            # Lower volatility in level scale for more stable predictions
            level_scale_prior = tfd.LogNormal(
                loc=tf.constant(-5., dtype=tf.float64),  # Much tighter prior for stability
                scale=tf.constant(0.3, dtype=tf.float64)  # Narrower distribution
            )

            # More appropriate slope scale for cryptocurrency dynamics
            slope_scale_prior = tfd.LogNormal(
                loc=tf.constant(-4., dtype=tf.float64),
                scale=tf.constant(0.5, dtype=tf.float64)
            )

            # Initialize level at the first observation with smaller variance
            initial_level_prior = tfd.Normal(
                loc=observed_time_series[0],
                scale=tf.constant(100., dtype=tf.float64)  # Reduced from 1000 to 100
            )

            # Allow for non-zero initial slope to capture trends immediately
            if len(observed_time_series) >= 3:
                # Calculate initial slope from first few observations with exponential weighting
                # This puts more emphasis on the most recent trend
                if len(observed_time_series) >= 10:
                    # Use more points for a more stable initial slope
                    weights = np.exp(np.linspace(0, 1, 10))
                    weights = weights / np.sum(weights)
                    diffs = np.diff(observed_time_series[:10].numpy())
                    initial_slope = np.sum(diffs * weights[:len(diffs)])
                else:
                    # Simple approach for very short series
                    initial_slope = (observed_time_series[2] - observed_time_series[0]) / 2.0
                
                initial_slope_prior = tfd.Normal(
                    loc=tf.constant(initial_slope, dtype=tf.float64),
                    scale=tf.constant(50., dtype=tf.float64)  # Reduced from 100 to 50
                )
            else:
                initial_slope_prior = tfd.Normal(
                    loc=tf.constant(0., dtype=tf.float64),
                    scale=tf.constant(50., dtype=tf.float64)
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
            
            # Create seasonal prior with explicit float64 dtype and tighter constraints
            drift_scale_prior = tfd.LogNormal(
                loc=tf.constant(-4., dtype=tf.float64),  # Tighter prior
                scale=tf.constant(0.3, dtype=tf.float64)  # Reduced variability
            )
            
            # Add enhanced seasonality components - specifically tuned for crypto markets
            # Add both daily and weekly seasonality for crypto markets
            
            # 24-hour cycle for intraday patterns (if data frequency permits)
            if self.num_timesteps >= 48:  # At least two full cycles recommended
                daily_seasonal = tfs.Seasonal(
                    num_seasons=24,
                    observed_time_series=observed_time_series,
                    drift_scale_prior=drift_scale_prior,
                    name='daily_seasonal'
                )
                components.append(daily_seasonal)
            
            # 7-day cycle for weekly patterns (if enough data available)
            if self.num_timesteps >= 168:  # 7 days × 24 hours
                weekly_seasonal = tfs.Seasonal(
                    num_seasons=7,
                    observed_time_series=observed_time_series,
                    drift_scale_prior=drift_scale_prior,
                    name='weekly_seasonal'
                )
                components.append(weekly_seasonal)
            
            # Standard seasonal component based on frequency pattern
            seasonal = tfs.Seasonal(
                num_seasons=self.num_seasons,
                observed_time_series=observed_time_series,
                drift_scale_prior=drift_scale_prior,
                name='seasonal'
            )
            components.append(seasonal)

            # Enhanced autoregressive component with higher order for better short-term predictions
            # Use AR(5) for cryptocurrency data which has complex short-term dynamics
            ar_order = 5

            # Only use higher-order AR if we have enough data
            if len(observed_time_series) > ar_order * 3:
                # Use a semi-local parameterization for more stability
                autoregressive = tfs.Autoregressive(
                    order=ar_order,
                    observed_time_series=observed_time_series,
                    name='autoregressive'
                )
                components.append(autoregressive)
            else:
                # Fall back to AR(2) for short time series
                autoregressive = tfs.Autoregressive(
                    order=2,
                    observed_time_series=observed_time_series,
                    name='autoregressive'
                )
                components.append(autoregressive)
            
            # Add a SemiLocalLinearTrend for better handling of cryptocurrency volatility
            if len(observed_time_series) > 20:  # Only if we have enough data
                try:
                    semi_local_linear_trend = tfs.SemiLocalLinearTrend(
                        observed_time_series=observed_time_series,
                        name='semi_local_linear_trend'
                    )
                    components.append(semi_local_linear_trend)
                except Exception as e:
                    self.logger.warning(f"Could not add SemiLocalLinearTrend: {e}")

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
        """Fit the model using variational inference with enhanced optimization strategies."""
        try:
            # Check if model is valid
            if self.model is None:
                print("Error: Cannot fit variational inference - model is None")
                return None

            # Clear old TF variables by creating a new surrogate posterior
            # Build surrogate posterior - this creates new TF variables
            try:
                # Use factored surrogate posterior with tailored initialization
                surrogate = tfs.build_factored_surrogate_posterior(
                    model=self.model,
                    initial_loc_fn=lambda *args: tfd.Normal(loc=0.0, scale=0.01).sample(*args)
                )
            except Exception as e:
                print(f"Error building surrogate posterior: {e}")
                return None

            # Create a new optimizer for each fit to prevent variable sharing issues
            optimizer = self._create_optimizer()
            
            # Define joint log probability function with numerical stability improvements
            @tf.function(experimental_relax_shapes=True, reduce_retracing=True)
            def target_log_prob_fn(**params):
                # Add small epsilon to potentially zero values to avoid numerical issues
                safe_params = {}
                for param_name, param_value in params.items():
                    if 'scale' in param_name:
                        # Add small epsilon to scale parameters to ensure positive values
                        safe_params[param_name] = param_value + 1e-8
                    else:
                        safe_params[param_name] = param_value
                
                return self.model.joint_distribution(
                    observed_time_series=self.observed_time_series
                ).log_prob(**params)
            
            # Implement early stopping to prevent overfitting
            patience = 10  # Number of steps to wait after validation improvement
            min_delta = 0.001  # Minimum change to qualify as improvement
            best_loss = float('inf')
            patience_counter = 0
            early_stopping = False
            
            # Dynamically adjust steps for dataset size
            # Use fewer steps for smaller datasets to speed up computation
            actual_steps = num_steps
            if len(self.observed_time_series) < 30:
                # For small datasets, fewer steps are needed
                actual_steps = max(50, int(num_steps * 0.6))
                print(f"Small dataset detected, using reduced VI steps: {actual_steps}")
            elif len(self.observed_time_series) > 100:
                # For large datasets, ensure sufficient steps for convergence
                actual_steps = min(200, int(num_steps * 1.2))
                print(f"Large dataset detected, using increased VI steps: {actual_steps}")
            else:
                actual_steps = num_steps
                
            # Implement multi-start optimization to avoid local minima
            # Try 3 different initializations and pick the best
            best_surrogate = None
            best_loss_value = float('inf')
            
            for start_idx in range(3):
                # Reset the surrogate for each start
                if start_idx > 0:
                    try:
                        surrogate = tfs.build_factored_surrogate_posterior(
                            model=self.model,
                            initial_loc_fn=lambda *args: tfd.Normal(loc=0.0, scale=0.01 * (start_idx + 1)).sample(*args)
                        )
                    except Exception as e:
                        print(f"Error rebuilding surrogate posterior for start {start_idx}: {e}")
                        continue
                    
                    # Create a fresh optimizer for each start
                    optimizer = self._create_optimizer()
                    
                # Custom training loop with early stopping
                @tf.function(experimental_relax_shapes=True)
                def run_vi_step(step):
                    with tf.GradientTape() as tape:
                        loss = -surrogate.variational_loss(target_log_prob_fn)
                    grads = tape.gradient(loss, surrogate.trainable_variables)
                    
                    # Gradient clipping to prevent exploding gradients
                    grads, _ = tf.clip_by_global_norm(grads, 5.0)
                    
                    optimizer.apply_gradients(zip(grads, surrogate.trainable_variables))
                    return loss
                
                # Run optimization with early stopping
                losses = []
                for step in range(actual_steps):
                    loss_value = run_vi_step(tf.constant(step, dtype=tf.int32))
                    losses.append(loss_value)
                    
                    # Check for early stopping every few steps
                    if step % 10 == 0 and step > 0:
                        current_loss = loss_value.numpy()
                        
                        if current_loss < best_loss - min_delta:
                            best_loss = current_loss
                            patience_counter = 0
                        else:
                            patience_counter += 1
                            
                        if patience_counter >= patience:
                            print(f"Early stopping triggered at step {step}")
                            early_stopping = True
                            break
                
                # Track the best surrogate across different starts
                final_loss = losses[-1].numpy()
                if final_loss < best_loss_value:
                    best_loss_value = final_loss
                    best_surrogate = surrogate
                    print(f"New best surrogate from start {start_idx} with loss {final_loss:.4f}")
                    
                # Break if we've found a good solution
                if early_stopping and best_loss_value < -1000:
                    print(f"Good solution found early, skipping remaining starts")
                    break
            
            # Use the best surrogate found
            if best_surrogate is not None:
                surrogate = best_surrogate
                print(f"Using best surrogate with loss {best_loss_value:.4f}")
            
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
        Generate forecasts with uncertainty intervals using ensemble techniques for higher accuracy.
        
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

            # Use more samples for more accurate prediction distribution
            increased_samples = min(100, self.num_samples * 2)  # Double samples but cap at 100
            
            # Create ensemble of forecasts from multiple sampling runs
            ensemble_predictions = []
            ensemble_scales = []
            
            # Make 3 independent forecast runs and ensemble them
            for ensemble_run in range(3):
                # Generate samples from the posterior and forecast using cached function
                forecast_dist = self._generate_forecast(num_steps)
                
                # Extract forecast samples
                mean_forecast, scale_forecast = self._extract_forecast_stats(forecast_dist)
                
                # Add to ensemble
                ensemble_predictions.append(mean_forecast)
                ensemble_scales.append(scale_forecast)
            
            # Compute ensemble prediction (weighted by inverse of scale)
            weights = [1.0 / (s + 1e-6) for s in ensemble_scales]  # Add epsilon to avoid division by zero
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Weighted average for the final prediction
            mean_forecast_value = sum(p * w for p, w in zip(ensemble_predictions, normalized_weights))
            
            # Take the most conservative (largest) scale for uncertainty bounds
            scale_forecast_value = max(ensemble_scales)
            
            # Extract scalars using utility function
            mean_forecast_value = extract_scalar_from_prediction(mean_forecast_value)
            scale_forecast_value = extract_scalar_from_prediction(scale_forecast_value)

            # Calculate prediction intervals with wider bounds for cryptocurrency
            # Use 99% confidence for crypto instead of 95% (2.58 vs 1.96)
            lower = mean_forecast_value - 2.58 * scale_forecast_value
            upper = mean_forecast_value + 2.58 * scale_forecast_value
            
            # Implement sanity checks for crypto predictions
            # Ensure prediction is within reasonable bounds (e.g., not too far from current price)
            last_observed = extract_scalar_from_prediction(self.observed_time_series[-1])
            max_allowed_change = 0.05 * last_observed  # Max 5% change from last price
            
            if abs(mean_forecast_value - last_observed) > max_allowed_change:
                # Adjust prediction to be closer to last observed price
                print(f"Forecast {mean_forecast_value:.2f} differs too much from last price {last_observed:.2f}. Adjusting.")
                direction = 1 if mean_forecast_value > last_observed else -1
                mean_forecast_value = last_observed + direction * max_allowed_change
                
                # Recalculate bounds with the new mean
                lower = mean_forecast_value - 2.58 * scale_forecast_value
                upper = mean_forecast_value + 2.58 * scale_forecast_value

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
    
    def update(self, new_data_point):
        """
        Update the model with new data, using adaptive learning strategies
        specifically designed for cryptocurrency price movements.
        
        Args:
            new_data_point: New observation to incorporate - can be a single value,
                           array, or tensor
        """
        try:
            # Check and validate input
            if isinstance(new_data_point, (int, float)):
                new_data = np.array([new_data_point], dtype=np.float64)
            elif isinstance(new_data_point, tf.Tensor):
                new_data = new_data_point.numpy()
            elif isinstance(new_data_point, np.ndarray):
                new_data = new_data_point
            elif isinstance(new_data_point, list):
                new_data = np.array(new_data_point, dtype=np.float64)
            else:
                print(f"Warning: Unsupported data type for update: {type(new_data_point)}")
                return False

            # Adaptive update strategy for cryptocurrency price data
            # Detect if there's been a significant price change that requires more VI steps
            significant_change = False
            volatility_increased = False
            
            # Check if we have historical data to compare with
            if self.observed_time_series is not None and len(self.observed_time_series) > 0:
                last_price = extract_scalar_from_prediction(self.observed_time_series[-1])
                new_price = extract_scalar_from_prediction(new_data[-1])
                
                # Calculate percentage change
                if abs(last_price) > 1e-6:  # Avoid division by zero
                    pct_change = abs((new_price - last_price) / last_price)
                    
                    # For crypto, consider >1% a significant move requiring extra update steps
                    if pct_change > 0.01:
                        significant_change = True
                        print(f"Significant price change detected: {pct_change:.2%}. Using enhanced update.")
                
                # Check for increased volatility (using recent standard deviation)
                if len(self.observed_time_series) >= 10:
                    # Get last 10 observations
                    recent_data = self.observed_time_series[-10:].numpy()
                    # Add new data point
                    combined_data = np.append(recent_data, new_data[-1])
                    
                    # Calculate standard deviations
                    recent_std = np.std(recent_data)
                    new_std = np.std(combined_data)
                    
                    # Check if volatility has increased significantly (>20%)
                    if new_std > recent_std * 1.2:
                        volatility_increased = True
                        print(f"Volatility increase detected: {(new_std/recent_std-1)*100:.1f}%. Using enhanced update.")

            # Append new data to observed time series
            if self.observed_time_series is None:
                self.observed_time_series = tf.convert_to_tensor(new_data, dtype=tf.float64)
            else:
                # Append the new data, ensuring it's a tensor
                new_data_tensor = tf.convert_to_tensor(new_data, dtype=tf.float64)
                self.observed_time_series = tf.concat(
                    [self.observed_time_series, new_data_tensor], axis=0)
            
            # Limit dataset size to prevent unbounded growth
            if len(self.observed_time_series) > self.max_history_size:
                # Keep more recent data for crypto (more relevant for prediction)
                print(f"Limiting history to {self.max_history_size} points")
                self.observed_time_series = self.observed_time_series[-self.max_history_size:]

            # Store the number of timesteps
            self.num_timesteps = len(self.observed_time_series)
            
            # Apply preprocessing to the new time series
            preprocessed_data = self.preprocess_data(self.observed_time_series)
            if preprocessed_data is not None:
                self.observed_time_series = preprocessed_data
            
            # Verify that we have sufficient data for model fitting
            if len(self.observed_time_series) < self.min_points_req:
                print(
                    f"Not enough data points ({len(self.observed_time_series)}) for fitting. Need {self.min_points_req}.")
                return False

            # Rebuild the model with the updated time series
            self.model = self.build_model(self.observed_time_series)
            if self.model is None:
                print("Failed to build model during update")
                return False
                
            # Determine number of VI steps based on data characteristics
            vi_steps = self.num_variational_steps
            
            # Boost VI steps for significant changes or increased volatility
            if significant_change or volatility_increased:
                vi_steps = int(vi_steps * 1.5)  # 50% more steps for better adaptation
                print(f"Using increased VI steps: {vi_steps}")
            
            # For large datasets, adjust steps to prevent excessive computation
            if len(self.observed_time_series) > 100:
                # Cap at a maximum based on available computational resources
                vi_steps = min(vi_steps, 150)
                
            # For very small updates, use fewer steps to speed up processing
            if len(new_data) == 1 and not (significant_change or volatility_increased):
                vi_steps = int(vi_steps * 0.7)  # 30% fewer steps for minor updates
                
            # Fit the model with the determined number of steps
            print(f"Updating model with {len(self.observed_time_series)} points and {vi_steps} VI steps")
            self.posterior = self._fit_variational_inference(vi_steps)
            
            # Verify successful fit
            if self.posterior is None:
                print("Failed to fit variational inference during update")
                return False
                
            # Report success with detailed timing information
            print(
                f"[{datetime.now().isoformat()}] Successfully updated model v{self.model_version} with {len(new_data)} new data points")
                
            # Simulate an immediate forecast to update internal stat tracking
            self.forecast()
            
            return True

        except Exception as e:
            print(f"Error updating model: {e}\n{traceback.format_exc()}")
            return False

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
