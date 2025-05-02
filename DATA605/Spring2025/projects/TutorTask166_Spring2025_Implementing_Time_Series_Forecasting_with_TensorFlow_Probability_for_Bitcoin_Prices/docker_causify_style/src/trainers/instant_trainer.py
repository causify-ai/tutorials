import logging
from typing import Dict
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class InstantTrainer:
    def __init__(
        self,
        loader,
        fe,
        model,
        logger,
        config,
    ):
        self.loader = loader
        self.fe = fe
        self.model = model
        self.logger = logger
        self.config = config
        
        # Update config access to match new structure
        self.predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        self.metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        self.raw_data_file = config['data']['raw_data']['instant_data']['file']
        
        # Model parameters
        self.evaluation_window = config['model']['instant']['evaluation_window']
        self.forecast_horizon = config['model']['instant']['forecast_horizon']
        
        # Kafka settings
        self.kafka_bootstrap_servers = config['kafka']['bootstrap_servers']
        self.kafka_topic = config['kafka']['topic']

    def evaluate_model(self, series: pd.DataFrame, forecast_dist) -> Dict[str, float]:
        """
        Evaluate model performance on historical data.
        This is separate from the model training process and is used for monitoring only.
        """
        # Get actual values for the forecast horizon
        actual_values = series['close'].iloc[-self.forecast_horizon:].values
        
        # Get predicted values and ensure we only take the requested number of steps
        samples = forecast_dist.sample(1000)  # Shape: (1000, forecast_horizon, 1)
        predicted_mean = tf.reduce_mean(samples, axis=0).numpy()[:self.forecast_horizon, 0]  # Take first dimension
        
        # Calculate metrics
        return {
            'rmse': np.sqrt(mean_squared_error(actual_values, predicted_mean)),
            'mae': mean_absolute_error(actual_values, predicted_mean),
            'mape': np.mean(np.abs((actual_values - predicted_mean) / actual_values)) * 100,
            'r2': r2_score(actual_values, predicted_mean)
        }

    def save_metrics(self, metrics: Dict[str, float]):
        """Save evaluation metrics to CSV file."""
        df = pd.DataFrame([metrics])
        df['timestamp'] = pd.Timestamp.now()
        df.to_csv(self.metrics_file, mode='a', header=not pd.io.common.file_exists(self.metrics_file), index=False)

    def save_predictions(self, predictions: Dict[str, np.ndarray]):
        """Save predictions to CSV file."""
        # Create a single row with the current timestamp and the first prediction values
        df = pd.DataFrame({
            'timestamp': [pd.Timestamp.now()],
            'mean': [predictions['mean'][0]],  # Take first value
            'lower': [predictions['lower'][0]],  # Take first value
            'upper': [predictions['upper'][0]]  # Take first value
        })
        df.to_csv(self.predictions_file, mode='a', header=not pd.io.common.file_exists(self.predictions_file), index=False)

    def run(self) -> Dict[str, float]:
        # 1) load raw
        raw = self.loader.fetch()
        self.logger.info(f"Loaded {len(raw)} raw instant rows")

        # 2) features
        series = self.fe.transform(raw)
        self.logger.info(f"Transformed into {len(series)} feature rows")

        # 3) fit model using TFP's VI
        self.model.fit(series)
        self.logger.info("Instant model fit complete")

        # 4) forecast
        forecast_dist = self.model.forecast(self.forecast_horizon)
        self.logger.info(f"Forecasted next {self.forecast_horizon} steps")

        # 5) extract stats using samples
        samples = forecast_dist.sample(1000)  # Shape: (1000, forecast_horizon, 1)
        mean = tf.reduce_mean(samples, axis=0).numpy()[:self.forecast_horizon, 0]  # Take first dimension
        lower = tfp.stats.percentile(samples, 10.0, axis=0).numpy()[:self.forecast_horizon, 0]
        upper = tfp.stats.percentile(samples, 90.0, axis=0).numpy()[:self.forecast_horizon, 0]
        
        # 6) Evaluate model performance (separate from training)
        metrics = self.evaluate_model(series, forecast_dist)
        self.logger.info(f"Model Evaluation Metrics: {metrics}")
        self.save_metrics(metrics)
        
        # 7) Save predictions
        predictions = {'mean': mean, 'lower': lower, 'upper': upper}
        self.save_predictions(predictions)
        
        self.logger.info(f"Mean (head): {mean[:5]}")
        self.logger.info(f"90% CI lower (head): {lower[:5]}")
        self.logger.info(f"90% CI upper (head): {upper[:5]}")

        return predictions