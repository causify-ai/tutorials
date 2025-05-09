import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from utilities.logger import get_logger
import traceback

class InstantForecastModel:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.posterior = None
        self.observed_time_series = None
        self.observed_timestamps = None  # Store timestamps separately
        self.window_size = timedelta(minutes=5)  # 5-minute window for predictions
        self.last_prediction_time = None
        self.logger = get_logger(__name__)
        self.loader = None  # Will be set externally

        # ── seed with any existing raw CSV on disk ──
        hist_file = config['data']['raw_data']['instant_data']['file']
        try:
            df_hist = pd.read_csv(hist_file, parse_dates=['timestamp'])
            if not df_hist.empty:
                self.observed_time_series = df_hist['close']
                self.observed_timestamps  = df_hist['timestamp']
                self.logger.info(f"Initialized model with {len(df_hist)} historical records")
        except Exception as e:
            self.logger.warning(f"Could not load historical data '{hist_file}': {e}")

    def set_loader(self, loader):
        self.loader = loader

    def update_from_loader(self):
        if self.loader is not None:
            try:
                df = self.loader.fetch()
                if df is not None and not df.empty:
                    self.observed_time_series = df['close']
                    self.observed_timestamps = df['timestamp']
            except Exception as e:
                self.logger.error(f"Failed to update model data from loader: {e}")

    def fit(self, series, timestamps=None):
        """Fit the model with the given time series data."""
        self.observed_time_series = series
        # only overwrite timestamps if new ones are provided
        if timestamps is not None:
            self.observed_timestamps = timestamps
        sts_model = tfp.sts.LocalLinearTrend(observed_time_series=series)
        self.model = sts_model
        surrogate = tfp.sts.build_factored_surrogate_posterior(model=sts_model)
        def target_log_prob_fn(**params):
            return self.model.joint_distribution(
                observed_time_series=series
            ).log_prob(**params)
        losses = tfp.vi.fit_surrogate_posterior(
            target_log_prob_fn=target_log_prob_fn,
            surrogate_posterior=surrogate,
            optimizer=tf.optimizers.Adam(
                learning_rate=self.config['model']['instant']['learning_rate']
            ),
            num_steps=self.config['model']['instant']['vi_steps']
        )
        self.posterior = surrogate
        return surrogate

    def should_predict(self, current_time):
        """Check if we should make a new prediction based on the current time."""
        if self.last_prediction_time is None:
            return True
        # Convert current_time to datetime if it's a timestamp
        if isinstance(current_time, (int, float)):
            current_time = pd.Timestamp(current_time, unit='s')
        # Convert last_prediction_time to datetime if it's a timestamp
        if isinstance(self.last_prediction_time, (int, float)):
            self.last_prediction_time = pd.Timestamp(self.last_prediction_time, unit='s')
        # Make a new prediction every second
        return (current_time - self.last_prediction_time).total_seconds() >= 1

    def forecast(self, current_time):
        """Make a single-step forecast for the next second."""
        # Always update from loader before forecasting
        self.update_from_loader()
        # Convert current_time to pandas Timestamp if it's a Unix timestamp
        if isinstance(current_time, (int, float)):
            current_time = pd.Timestamp(current_time, unit='s')
        if not self.should_predict(current_time):
            return None
        # Calculate window start time
        window_start = current_time - self.window_size
        window_data = None
        timestamps = None
        # If we have timestamps, filter the data
        if self.observed_timestamps is not None and self.observed_time_series is not None:
            # Defensive: ensure lengths match and are > 1
            if len(self.observed_timestamps) != len(self.observed_time_series) or len(self.observed_time_series) < 2:
                self.logger.warning("Observed timestamps and series length mismatch or too short. Skipping prediction.")
                return None
            # Convert timestamps to pandas Timestamps if they aren't already
            if not isinstance(self.observed_timestamps[0], pd.Timestamp):
                timestamps = pd.to_datetime(self.observed_timestamps, errors='coerce')
            else:
                timestamps = self.observed_timestamps
            # Drop any NaT timestamps
            valid_mask = ~pd.isnull(timestamps)
            timestamps = timestamps[valid_mask]
            window_data = self.observed_time_series[valid_mask]
            # Get indices of data points within the window
            mask = timestamps >= window_start
            window_data = window_data[mask]
            timestamps = timestamps[mask]
            # Defensive: check again
            if len(window_data) < 2:
                self.logger.info("Not enough valid data in window for prediction. Skipping.")
                return None
        else:
            # If no timestamps, use all available data
            window_data = self.observed_time_series
            if window_data is None or (hasattr(window_data, '__len__') and len(window_data) < 2):
                self.logger.info("No data available for prediction. Waiting for more data...")
                return None
            timestamps = None
        # Fit the model with the window data _and_ update our timestamp index
        self.fit(window_data, timestamps=timestamps)
        # Make a single-step forecast
        try:
            samples = self.posterior.sample(self.config['model']['instant']['num_samples'])
            forecast_dist = tfp.sts.forecast(
                model=self.model,
                observed_time_series=window_data,
                parameter_samples=samples,
                num_steps_forecast=1
            )
        except Exception as e:
            self.logger.error(f"Forecasting failed: {e}\n{traceback.format_exc()}")
            return None
        # Update last prediction time
        self.last_prediction_time = current_time
        # Return both the distribution and metadata (always use intended forecast time)
        try:
            return {
                'distribution': forecast_dist,
                'metadata': {
                    'timestamp': to_iso8601(current_time),
                    'mean': float(forecast_dist.mean()[0]),
                    'std': float(forecast_dist.stddev()[0]),
                    'lower': float(forecast_dist.mean()[0] - 1.645 * forecast_dist.stddev()[0]),
                    'upper': float(forecast_dist.mean()[0] + 1.645 * forecast_dist.stddev()[0])
                }
            }
        except Exception as e:
            self.logger.error(f"Error extracting forecast metadata: {e}\n{traceback.format_exc()}")
            return None