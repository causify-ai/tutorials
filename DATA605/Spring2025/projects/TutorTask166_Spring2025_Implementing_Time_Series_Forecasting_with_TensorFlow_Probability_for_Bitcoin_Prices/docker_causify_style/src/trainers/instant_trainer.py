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
import traceback
from utilities.timestamp_format import to_iso8601
from utilities.logger import get_logger

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
        self.logger = logger if logger is not None else get_logger(__name__)
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

    def save_metrics(self, timestamp, std, mae, rmse):
        """Save metrics to CSV file using config-driven columns."""
        try:
            metrics_cols = self.config['data_format']['columns']['metrics']['names']
            metrics_row = {
                'timestamp': to_iso8601(timestamp),
                'std': float(std),
                'mae': float(mae),
                'rmse': float(rmse)
            }
            df = pd.DataFrame([metrics_row], columns=metrics_cols)
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            with open(self.metrics_file, 'a' if os.path.exists(self.metrics_file) else 'w') as f:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    if f.tell() == 0:
                        df.to_csv(f, index=False)
                    else:
                        df.to_csv(f, mode='a', header=False, index=False)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            self.logger.info(f"Saved metrics for {timestamp}")
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
            raise

    def save_prediction(self, timestamp, actual_price, predicted_price, confidence_interval):
        """Save prediction to CSV file using config-driven columns."""
        try:
            pred_cols = self.config['data_format']['columns']['predictions']['names']
            pred_row = {
                'timestamp': to_iso8601(timestamp),
                'pred_price': float(predicted_price),
                'pred_lower': float(confidence_interval[0]),
                'pred_upper': float(confidence_interval[1])
            }
            df = pd.DataFrame([pred_row], columns=pred_cols)
            os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
            with open(self.predictions_file, 'a' if os.path.exists(self.predictions_file) else 'w') as f:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    if f.tell() == 0:
                        df.to_csv(f, index=False)
                    else:
                        df.to_csv(f, mode='a', header=False, index=False)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            self.logger.info(f"Saved prediction for {timestamp}")
        except Exception as e:
            self.logger.error(f"Error saving prediction: {e}\nData: {pred_row}\n{traceback.format_exc()}")
            raise

    def append_to_csv(self, data, filename):
        """Append data to CSV file, creating it if it doesn't exist."""
        try:
            # Create DataFrame from data
            df = pd.DataFrame([data])
            
            # Filter columns based on file type
            if 'predictions' in filename:
                # For predictions file: timestamp, mean, lower, upper
                # pred_cols = self.config['data_format']['columns']['predictions']['names']  # TODO: the naming in config is different from the metadata keys defined above, thus hard code here
                df = df[['timestamp', 'mean', 'lower', 'upper']]
            elif 'metrics' in filename:
                # For metrics file: timestamp, std, mae, rmse
                # metrics_cols = self.config['data_format']['columns']['metrics']['names']  # TODO: the naming in config is different from the metadata keys defined above, thus hard code here
                df = df[['timestamp', 'std', 'mae', 'rmse']]
            
            if not os.path.exists(filename):
                df.to_csv(filename, index=False)
                self.logger.info(f"Created new file: {filename}")
            else:
                df.to_csv(filename, mode='a', header=False, index=False)
                self.logger.debug(f"Appended data to: {filename}")
        except Exception as e:
            self.logger.error(f"Error appending to {filename}: {str(e)}")

    def buffer_kafka_message(self, message):
        buffer_file = "kafka_failed_buffer.jsonl"
        try:
            with open(buffer_file, "a") as f:
                f.write(json.dumps(message) + "\n")
            self.logger.warning("Buffered Kafka message to disk.")
        except Exception as e:
            self.logger.error(f"Failed to buffer Kafka message: {e}")

    def resend_buffered_kafka_messages(self):
        buffer_file = "kafka_failed_buffer.jsonl"
        if not os.path.exists(buffer_file):
            return
        lines_to_keep = []
        try:
            with open(buffer_file, "r") as f:
                for line in f:
                    try:
                        msg = json.loads(line)
                        self.producer.send(self.kafka_topic, value=msg)
                        self.producer.flush()
                    except Exception as e:
                        self.logger.error(f"Failed to resend buffered Kafka message: {e}")
                        lines_to_keep.append(line)
            # Rewrite buffer file with unsent messages
            with open(buffer_file, "w") as f:
                f.writelines(lines_to_keep)
        except Exception as e:
            self.logger.error(f"Error processing Kafka buffer file: {e}")

    def backup_failed_row(self, row, backup_file, kind='predictions'):
        try:
            if kind == 'predictions':
                cols = self.config['data_format']['columns']['predictions']['names']
            elif kind == 'metrics':
                cols = self.config['data_format']['columns']['metrics']['names']
            else:
                cols = list(row.keys())
            # Fill missing columns with NaN
            for col in cols:
                if col not in row:
                    row[col] = float('nan')
            df = pd.DataFrame([row], columns=cols)
            if not os.path.exists(backup_file):
                df.to_csv(backup_file, index=False)
            else:
                df.to_csv(backup_file, mode='a', header=False, index=False)
            self.logger.warning(f"Backed up failed row to {backup_file}")
        except Exception as e:
            self.logger.error(f"Failed to backup row: {e}")

    def run(self):
        self.logger.info("Starting continuous predictions...")

        while True:
            try:
                # Try to resend any buffered Kafka messages first
                self.resend_buffered_kafka_messages()

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

                # Save prediction and metrics with error handling and backup
                try:
                    self.save_prediction(
                        timestamp=metadata['timestamp'],
                        actual_price=None,
                        predicted_price=metadata['mean'],
                        confidence_interval=(metadata['lower'], metadata['upper'])
                    )
                except Exception as e:
                    self.logger.error(f"Error saving prediction: {e}")
                    self.backup_failed_row(
                        {
                            'timestamp': metadata['timestamp'],
                            'pred_price': metadata['mean'],
                            'pred_lower': metadata['lower'],
                            'pred_upper': metadata['upper']
                        },
                        "failed_predictions_backup.csv",
                        kind='predictions'
                    )

                try:
                    self.save_metrics(
                        timestamp=metadata['timestamp'],
                        std=metadata['std'],
                        mae=metrics['mae'],
                        rmse=metrics['rmse']
                    )
                except Exception as e:
                    self.logger.error(f"Error saving metrics: {e}")
                    self.backup_failed_row(
                        {
                            'timestamp': metadata['timestamp'],
                            'std': metadata['std'],
                            'mae': metrics['mae'],
                            'rmse': metrics['rmse']
                        },
                        "failed_metrics_backup.csv",
                        kind='metrics'
                    )

                # Send to Kafka with error handling and buffer fallback
                try:
                    self.producer.send(self.kafka_topic, value=metadata)
                    self.producer.flush()
                except Exception as e:
                    self.logger.error(f"Error sending to Kafka: {e}")
                    self.buffer_kafka_message(metadata)

                self.logger.info(f"Prediction made for {current_time}: mean={metadata['mean']:.2f}, std={metadata['std']:.2f}")

                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in prediction loop: {str(e)}")
                time.sleep(1)
                continue