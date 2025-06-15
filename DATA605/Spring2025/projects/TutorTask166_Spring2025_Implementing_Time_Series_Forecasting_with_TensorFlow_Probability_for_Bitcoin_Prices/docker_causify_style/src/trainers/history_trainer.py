from utilities.logger import get_logger
import tensorflow as tf
import tensorflow_probability as tfp
import pandas as pd
import os
from utilities.timestamp_format import to_iso8601

class HistoryTrainer:
    def __init__(
        self,
        loader,
        feature_engineer,
        model,
        logger,
        config: dict,
    ):
        self.loader = loader
        self.fe = feature_engineer
        self.model = model
        self.logger = logger if logger is not None else get_logger(__name__)
        self.config = config
        self.horizon = config['history']['forecast_horizon']

    def run(self):
        raw = self.loader.fetch()
        self.logger.info(f"Loaded {len(raw)} raw history rows")

        series = self.fe.transform(raw)
        self.logger.info(f"Transformed into {len(series)} feature rows")

        # only target series (e.g. price)
        self.model.fit(series['price'])
        self.logger.info("History model fit complete")

        forecast_dist = self.model.forecast(self.horizon)
        self.logger.info(f"Forecasted next {self.horizon} days")

        # Extract stats using samples since quantile is not implemented
        samples = forecast_dist.sample(1000)  # Get 1000 samples for better estimation
        mean = tf.reduce_mean(samples, axis=0).numpy()
        lower = tfp.stats.percentile(samples, 10.0, axis=0).numpy()
        upper = tfp.stats.percentile(samples, 90.0, axis=0).numpy()
        
        self.logger.info(f"Mean (head): {mean[:5]}")
        self.logger.info(f"90% CI lower (head): {lower[:5]}")
        self.logger.info(f"90% CI upper (head): {upper[:5]}")

        self.save_history_prediction(raw[-1]['timestamp'], mean, lower, upper)
        return {'mean': mean, 'lower': lower, 'upper': upper}

    def save_history_prediction(self, timestamp, mean, lower, upper):
        """Save history prediction to CSV file using config-driven columns."""
        pred_cols = self.config['data_format']['columns']['predictions']['names']
        pred_row = {
            'timestamp': to_iso8601(timestamp),
            'pred_price': float(mean),
            'pred_lower': float(lower),
            'pred_upper': float(upper)
        }
        df = pd.DataFrame([pred_row], columns=pred_cols)
        predictions_file = self.config['data']['predictions']['history_data']['predictions_file']
        os.makedirs(os.path.dirname(predictions_file), exist_ok=True)
        df.to_csv(predictions_file, mode='a', header=not os.path.exists(predictions_file), index=False)
        self.logger.info(f"Saved history prediction for {timestamp}")

    def save_history_metrics(self, timestamp, std, mae, rmse):
        """Save history metrics to CSV file using config-driven columns."""
        metrics_cols = self.config['data_format']['columns']['metrics']['names']
        metrics_row = {
            'timestamp': to_iso8601(timestamp),
            'std': float(std),
            'mae': float(mae),
            'rmse': float(rmse)
        }
        df = pd.DataFrame([metrics_row], columns=metrics_cols)
        metrics_file = self.config['data']['predictions']['history_data']['metrics_file']
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
        df.to_csv(metrics_file, mode='a', header=not os.path.exists(metrics_file), index=False)
        self.logger.info(f"Saved history metrics for {timestamp}")