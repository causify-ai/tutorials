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
        self.kafka_bootstrap_servers = self.config['kafka']['bootstrap_servers']
        self.kafka_topic = self.config['kafka']['topic']
        
        # Ensure predictions directory exists
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
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
            df = pd.read_csv(self.data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            # Ensure close price is float64
            df['close'] = df['close'].astype(np.float64)
            return df
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return pd.DataFrame()

    def save_prediction(self, timestamp, actual_price, predicted_price, confidence_interval):
        """Save prediction to CSV file."""
        try:
            prediction_data = {
                'timestamp': timestamp,
                'actual_price': float(actual_price),
                'predicted_price': float(predicted_price),
                'lower_bound': float(confidence_interval[0]),
                'upper_bound': float(confidence_interval[1])
            }
            
            # Create DataFrame
            df = pd.DataFrame([prediction_data])
            
            # Append to file if it exists, otherwise create new file
            if os.path.exists(self.predictions_file):
                df.to_csv(self.predictions_file, mode='a', header=False, index=False)
            else:
                df.to_csv(self.predictions_file, index=False)
            
            logger.info(f"Saved prediction for {timestamp}")
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")

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
                
                # Update model with new data
                self.model.update(price_series)
                
                # Generate forecast
                predicted_price, lower_bound, upper_bound = self.model.forecast()
                confidence_interval = (lower_bound, upper_bound)
                
                # Calculate metrics
                mae = abs(predicted_price - actual_price)
                rmse = np.sqrt(mae ** 2)
                mape = abs((predicted_price - actual_price) / actual_price) * 100
                
                # Save prediction and metrics
                self.save_prediction(timestamp, actual_price, predicted_price, confidence_interval)
                self.save_metrics(timestamp, mae, rmse, mape)
                
                logger.info(f"Made prediction for {timestamp}: Actual={actual_price:.2f}, Predicted={predicted_price:.2f}")
                return True
            else:
                logger.warning("No historical data available for prediction")
                return False
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return False

    def process_new_data(self, message):
        """Process new data from Kafka message."""
        try:
            data = message.value
            timestamp = pd.to_datetime(data['timestamp'])
            actual_price = np.float64(data['close'])  # Ensure float64
            
            # Make prediction
            self.make_prediction(timestamp, actual_price)
            
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