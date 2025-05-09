#!/usr/bin/env python3
"""
Real-time Bitcoin price forecasting using TensorFlow Probability.
Consumes data from Kafka and makes predictions.
"""
import os
import yaml
import json
import time
import logging
from datetime import datetime
import pandas as pd
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from utilities.timestamp_format import to_iso8601
from src.models.instant_model import InstantForecastModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load configuration
config_path = os.getenv('CONFIG_PATH', '/app/configs/config.yaml')
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Successfully loaded configuration from {config_path}")
except Exception as e:
    logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
    raise

# Initialize Kafka consumer
def init_kafka_consumer():
    try:
        consumer = KafkaConsumer(
            config['kafka']['topic'],
            bootstrap_servers=config['kafka']['bootstrap_servers'],
            group_id=config['kafka']['group_id'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        logger.info(f"Kafka bootstrap servers: {config['kafka']['bootstrap_servers']}")
        logger.info(f"Kafka topic: {config['kafka']['topic']}")
        return consumer
    except Exception as e:
        logger.error(f"Failed to initialize Kafka consumer: {e}")
        raise

def save_prediction(prediction, actual_price):
    try:
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        pred_cols = config['data_format']['columns']['predictions']['names']
        metrics_cols = config['data_format']['columns']['metrics']['names']
        os.makedirs(os.path.dirname(predictions_file), exist_ok=True)
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
        # Save prediction (only the new columns)
        pred_row = {
            'timestamp': prediction['metadata']['timestamp'],
            'pred_price': prediction['metadata']['mean'],
            'pred_lower': prediction['metadata']['lower'],
            'pred_upper': prediction['metadata']['upper']
        }
        df = pd.DataFrame([pred_row], columns=pred_cols)
        if os.path.exists(predictions_file):
            df.to_csv(predictions_file, mode='a', header=False, index=False)
        else:
            df.to_csv(predictions_file, index=False)
        logger.info(f"Saved prediction for {pred_row['timestamp']}")
        # Calculate and save metrics (std, mae, rmse) ONLY
        std = prediction['metadata']['std']
        mae = abs(actual_price - prediction['metadata']['mean'])
        rmse = mae  # Simplified for now
        metrics = {
            'timestamp': prediction['metadata']['timestamp'],
            'std': std,
            'mae': mae,
            'rmse': rmse
        }
        df_metrics = pd.DataFrame([metrics], columns=metrics_cols)
        if os.path.exists(metrics_file):
            df_metrics.to_csv(metrics_file, mode='a', header=False, index=False)
        else:
            df_metrics.to_csv(metrics_file, index=False)
        logger.info(f"Saved metrics for {metrics['timestamp']}")
        logger.info(f"Made prediction for {metrics['timestamp']}: Actual={actual_price:.2f}, Predicted={prediction['metadata']['mean']:.2f}")
    except Exception as e:
        logger.error(f"Failed to save prediction: {e}")
        raise

def main():
    logger.info("Starting robust Bitcoin price forecasting...")
    consumer = init_kafka_consumer()
    model = InstantForecastModel(config)
    try:
        while True:
            try:
                # Consume message from Kafka
                message = next(consumer)
                data = message.value
                # Parse timestamp
                timestamp = data.get('timestamp', datetime.now())
                if not isinstance(timestamp, datetime):
                    timestamp = pd.to_datetime(timestamp)
                # Append new data to model's rolling window
                price = float(data['price'])
                # Ensure type consistency
                if model.observed_time_series is None or model.observed_timestamps is None:
                    model.observed_time_series = pd.Series([price])
                    model.observed_timestamps = pd.Series([timestamp])
                else:
                    # Convert to pd.Series if needed
                    if not isinstance(model.observed_time_series, pd.Series):
                        model.observed_time_series = pd.Series(model.observed_time_series)
                    if not isinstance(model.observed_timestamps, pd.Series):
                        model.observed_timestamps = pd.Series(model.observed_timestamps)
                    model.observed_time_series = pd.concat([model.observed_time_series, pd.Series([price])], ignore_index=True)
                    model.observed_timestamps = pd.concat([model.observed_timestamps, pd.Series([timestamp])], ignore_index=True)
                logger.info(f"Rolling window length: {len(model.observed_time_series)} | Last price: {model.observed_time_series.iloc[-1]} | Last timestamp: {model.observed_timestamps.iloc[-1]}")
                # Forecast for the next time step
                prediction = model.forecast(timestamp)
                if prediction is not None:
                    save_prediction(prediction, price)
                else:
                    logger.warning("No forecast result available")
            except StopIteration:
                logger.warning("No more messages in Kafka")
                time.sleep(1)
            except KafkaError as e:
                logger.error(f"Kafka error: {e}")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main() 