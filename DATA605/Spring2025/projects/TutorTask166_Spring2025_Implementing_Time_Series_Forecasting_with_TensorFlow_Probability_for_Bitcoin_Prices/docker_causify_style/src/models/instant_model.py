import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import logging
from utilities.timestamp_format import to_iso8601, parse_timestamp

class InstantForecastModel:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.posterior = None
        self.observed_time_series = None
        self.observed_timestamps = None  # Store timestamps separately
        self.window_size = timedelta(minutes=5)  # 5-minute window for predictions
        self.last_prediction_time = None
        self.logger = logging.getLogger(__name__)

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
        # Convert current_time to pandas Timestamp if it's a Unix timestamp
        if isinstance(current_time, (int, float)):
            current_time = pd.Timestamp(current_time, unit='s')

        if not self.should_predict(current_time):
            return None

        # Calculate window start time
        window_start = current_time - self.window_size
        # If we have timestamps, filter the data
        if self.observed_timestamps is not None and self.observed_time_series is not None:
            # Convert timestamps to pandas Timestamps if they aren't already
            if not isinstance(self.observed_timestamps[0], pd.Timestamp):
                timestamps = pd.to_datetime(self.observed_timestamps, unit='s')
            else:
                timestamps = self.observed_timestamps
            # Get indices of data points within the window
            mask = timestamps >= window_start
            window_data = self.observed_time_series[mask]
        else:
            # If no timestamps, use all available data
            window_data = self.observed_time_series

        # Cold start: allow prediction with any available data
        if window_data is None or (hasattr(window_data, '__len__') and len(window_data) == 0):
            self.logger.info("No data available for prediction. Waiting for more data...")
            return None

        # # Fit the model with the window data
        # self.fit(window_data)  # FIXME: this will lead to forecaster dies after running for a while
        # Fit the model with the window data _and_ update our timestamp index
        self.fit(window_data,           # the prices
                 timestamps=timestamps)  # the matching pandas-DatetimeIndex

        # Make a single-step forecast
        samples = self.posterior.sample(self.config['model']['instant']['num_samples'])
        forecast_dist = tfp.sts.forecast(
            model=self.model,
            observed_time_series=window_data,
            parameter_samples=samples,
            num_steps_forecast=1
        )

        # Update last prediction time
        self.last_prediction_time = current_time

        # Return both the distribution and metadata (always use intended forecast time)
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