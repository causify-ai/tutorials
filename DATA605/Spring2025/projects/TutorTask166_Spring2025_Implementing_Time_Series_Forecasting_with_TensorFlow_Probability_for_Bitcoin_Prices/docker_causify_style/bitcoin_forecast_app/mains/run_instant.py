#!/usr/bin/env python3
"""
Bitcoin price forecasting application using TensorFlow Probability.
Loads real-time data from CSV and Kafka for continuous forecasting.
"""
import os
import json
import logging
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kafka import KafkaConsumer
import sys
import time
import concurrent.futures

# Add the models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.tfp_model import BitcoinForecastModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class BitcoinForecastApp:
    def __init__(self):
        # Load configuration
        with open('/app/configs/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.data_file = self.config['data']['raw_data']['instant_data']['file']
        self.predictions_file = self.config['data']['predictions']['instant_data']['predictions_file']
        self.metrics_file = self.config['data']['predictions']['instant_data']['metrics_file']
        
        # Use environment variables as fallback for Kafka configuration
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 
                                               self.config['kafka']['bootstrap_servers'])
        self.kafka_topic = os.getenv('KAFKA_TOPIC', 
                                   self.config['kafka']['topic'])
        
        # Ensure predictions directory exists
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='bitcoin-forecast-group',
            session_timeout_ms=60000,
            heartbeat_interval_ms=20000,
            max_poll_interval_ms=600000,
            retry_backoff_ms=1000,
            reconnect_backoff_ms=1000,
            reconnect_backoff_max_ms=5000,
            max_poll_records=100,
            fetch_max_wait_ms=500,
            fetch_min_bytes=1,
            fetch_max_bytes=52428800
        )
        
        # Initialize the TensorFlow Probability model
        self.model = BitcoinForecastModel()
        
        # Initialize last prediction time
        self.last_prediction_time = None
        
        logger.info(f"Initialized BitcoinForecastApp")
        logger.info(f"Data file: {self.data_file}")
        logger.info(f"Predictions file: {self.predictions_file}")
        logger.info(f"Metrics file: {self.metrics_file}")
        logger.info(f"Kafka bootstrap servers: {self.kafka_bootstrap_servers}")
        logger.info(f"Kafka topic: {self.kafka_topic}")

    def load_historical_data(self):
        """Load historical data from CSV file."""
        try:
            # Read CSV with proper column names
            df = pd.read_csv(
                self.data_file,
                names=['timestamp', 'open', 'high', 'low', 'close', 'volume'],
                skiprows=1  # Skip header row
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
            
            # Ensure numeric columns are float64
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            return df
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return pd.DataFrame()

    def save_prediction(self, timestamp, actual_price, predicted_price, confidence_interval):
        """Save prediction to CSV file."""
        try:
            # Format timestamp in ISO8601 format
            formatted_timestamp = pd.Timestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
            
            # Create prediction data
            prediction_data = {
                'timestamp': formatted_timestamp,
                'actual_price': float(actual_price),
                'predicted_price': float(predicted_price),
                'lower_bound': float(confidence_interval[0]),
                'upper_bound': float(confidence_interval[1])
            }
            
            # Save to CSV
            df = pd.DataFrame([prediction_data])
            df.to_csv(self.predictions_file, mode='a', header=not os.path.exists(self.predictions_file), index=False)
            
            logger.info(f"Saved prediction for {formatted_timestamp}")
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            raise

    def save_metrics(self, timestamp, mae, rmse, mape):
        """Save prediction metrics to CSV file."""
        try:
            metrics_data = {
                'timestamp': timestamp,
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape)
            }
            
            # Create DataFrame
            df = pd.DataFrame([metrics_data])
            
            # Append to file if it exists, otherwise create new file
            if os.path.exists(self.metrics_file):
                df.to_csv(self.metrics_file, mode='a', header=False, index=False)
            else:
                df.to_csv(self.metrics_file, index=False)
            
            logger.info(f"Saved metrics for {timestamp}")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    def make_prediction(self, timestamp, actual_price):
        """Make a prediction for the current timestamp."""
        try:
            # Get historical data for model input
            historical_data = self.load_historical_data()
            if not historical_data.empty:
                # Convert to numpy array for model input
                price_series = historical_data['close'].values
                
                # Only update model if we have new data
                if self.last_prediction_time is None or \
                   (timestamp - self.last_prediction_time).total_seconds() >= 60:  # Update every minute
                    self.model.update(price_series)
                    self.last_prediction_time = timestamp
                
                # Generate forecast
                predicted_price, lower_bound, upper_bound = self.model.forecast()
                confidence_interval = (lower_bound, upper_bound)
                
                # Calculate metrics
                mae = abs(predicted_price - actual_price)
                rmse = np.sqrt(mae ** 2)
                mape = abs((predicted_price - actual_price) / actual_price) * 100
                
                # Log the prediction with the timestamp
                logger.info(f"Made prediction for {timestamp}: Actual={actual_price:.2f}, Predicted={predicted_price:.2f}")
                
                # Save prediction and metrics in a single operation
                self.save_prediction_and_metrics(
                    timestamp,  # Use the same timestamp for saving
                    actual_price,
                    predicted_price,
                    confidence_interval,
                    mae,
                    rmse,
                    mape
                )
                
                return True
            else:
                logger.warning("No historical data available for prediction")
                return False
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return False

    def save_prediction_and_metrics(self, ts_make_prediction, actual_price, predicted_price, confidence_interval, mae, rmse, mape):
        """Save prediction and metrics in a single operation."""
        try:
            # Format the timestamp to match the data format
            formatted_ts = ts_make_prediction.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Prepare data with formatted timestamp
            prediction_data = {
                'timestamp': formatted_ts,  # Use formatted timestamp
                'actual_price': float(actual_price),
                'predicted_price': float(predicted_price),
                'lower_bound': float(confidence_interval[0]),
                'upper_bound': float(confidence_interval[1])
            }
            
            metrics_data = {
                'timestamp': formatted_ts,  # Use formatted timestamp
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape)
            }
            
            # Create DataFrames
            pred_df = pd.DataFrame([prediction_data])
            metrics_df = pd.DataFrame([metrics_data])
            
            # Save both files in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        lambda df, file: df.to_csv(file, mode='a', header=not os.path.exists(file), index=False),
                        pred_df, self.predictions_file
                    ),
                    executor.submit(
                        lambda df, file: df.to_csv(file, mode='a', header=not os.path.exists(file), index=False),
                        metrics_df, self.metrics_file
                    )
                ]
                concurrent.futures.wait(futures)
            
            logger.info(f"Saved prediction and metrics for {formatted_ts}")
            
        except Exception as e:
            logger.error(f"Error saving prediction and metrics: {e}")

    def process_new_data(self, message):
        """Process new data from Kafka message."""
        try:
            data = message.value
            # Capture the timestamp when we receive the message
            ts_make_prediction = datetime.now()
            actual_price = np.float64(data['close'])  # Ensure float64
            
            # Make prediction with the captured timestamp
            self.make_prediction(ts_make_prediction, actual_price)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def run(self):
        """Main loop to process incoming data."""
        logger.info("Starting Bitcoin price forecasting...")
        
        try:
            # Load initial historical data
            historical_data = self.load_historical_data()
            if not historical_data.empty:
                # Initialize model with historical data
                price_series = historical_data['close'].values
                self.model.fit(price_series)
                logger.info(f"Initialized model with {len(historical_data)} historical records")
            else:
                logger.warning("No historical data available for model initialization")
            
            # Process incoming messages
            for message in self.consumer:
                self.process_new_data(message)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise

if __name__ == "__main__":
    logger.info("Starting Bitcoin Forecast App...")
    app = BitcoinForecastApp()
    app.run() 