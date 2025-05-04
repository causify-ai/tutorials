import logging
from typing import Dict
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime, timedelta
import os
import time
from kafka import KafkaProducer
import json

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
        
        # Get file paths from config
        self.predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        self.metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        
        # Model parameters
        self.evaluation_window = config['model']['instant']['evaluation_window']
        self.forecast_horizon = config['model']['instant']['forecast_horizon']
        
        # Kafka settings
        self.kafka_bootstrap_servers = config['kafka']['bootstrap_servers']
        self.kafka_topic = config['kafka']['topic']

        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        self.logger.info(f"Initialized trainer with predictions file: {self.predictions_file}")
        self.logger.info(f"Initialized trainer with metrics file: {self.metrics_file}")

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

    def save_prediction(self, timestamp, actual_price, predicted_price, confidence_interval):
        """Save prediction to CSV file."""
        try:
            # Create a DataFrame with the prediction data
            prediction_data = {
                'timestamp': pd.Timestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),  # Remove microseconds
                'actual_price': float(actual_price),
                'predicted_price': float(predicted_price),
                'lower_bound': float(confidence_interval[0]),
                'upper_bound': float(confidence_interval[1])
            }
            
            # Create DataFrame with proper column order
            df = pd.DataFrame([prediction_data], columns=[
                'timestamp', 'actual_price', 'predicted_price', 'lower_bound', 'upper_bound'
            ])
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
            
            # Write to file with proper locking
            with open(self.predictions_file, 'a' if os.path.exists(self.predictions_file) else 'w') as f:
                # Get file lock
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    # Write header if file is new
                    if f.tell() == 0:
                        df.to_csv(f, index=False)
                    else:
                        df.to_csv(f, mode='a', header=False, index=False)
                finally:
                    # Release lock
                    fcntl.flock(f, fcntl.LOCK_UN)
            
            self.logger.info(f"Saved prediction for {timestamp}")
            
        except Exception as e:
            self.logger.error(f"Error saving prediction: {e}")
            raise

    def append_to_csv(self, data, filename):
        """Append data to CSV file, creating it if it doesn't exist."""
        try:
            df = pd.DataFrame([data])
            if not os.path.exists(filename):
                df.to_csv(filename, index=False)
                self.logger.info(f"Created new file: {filename}")
            else:
                df.to_csv(filename, mode='a', header=False, index=False)
                self.logger.debug(f"Appended data to: {filename}")
        except Exception as e:
            self.logger.error(f"Error appending to {filename}: {str(e)}")

    def run(self):
        """Run continuous predictions."""
        self.logger.info("Starting continuous predictions...")
        
        while True:
            try:
                # Get current time
                current_time = datetime.now()
                
                # Get latest data
                series = self.loader.load_latest_data()
                if series is None:
                    self.logger.info("Waiting for more data...")
                    time.sleep(1)
                    continue

                # Make prediction
                forecast_result = self.model.forecast(current_time)
                if forecast_result is None:
                    self.logger.warning("No forecast result available")
                    time.sleep(1)
                    continue

                # Extract distribution and metadata
                forecast_dist = forecast_result['distribution']
                metadata = forecast_result['metadata']

                # Get samples for metrics calculation
                samples = forecast_dist.sample(1000)  # Shape: (1000, 1, 1)
                samples = samples.numpy().squeeze()  # Shape: (1000,)

                # Calculate metrics
                metrics = {
                    'timestamp': metadata['timestamp'],
                    'mean': metadata['mean'],
                    'std': metadata['std'],
                    'lower': metadata['lower'],
                    'upper': metadata['upper'],
                    'mae': float(np.mean(np.abs(samples - metadata['mean']))),
                    'rmse': float(np.sqrt(np.mean((samples - metadata['mean'])**2)))
                }

                # Append predictions and metrics to CSV files
                self.append_to_csv(metadata, self.predictions_file)
                self.append_to_csv(metrics, self.metrics_file)

                # Send to Kafka
                self.producer.send(self.kafka_topic, value=metadata)
                self.producer.flush()

                self.logger.info(f"Prediction made for {current_time}: mean={metadata['mean']:.2f}, std={metadata['std']:.2f}")
                
                # Wait for next second
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in prediction loop: {str(e)}")
                time.sleep(1)
                continue