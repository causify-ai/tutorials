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
import gc

# Add the models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.tfp_model import BitcoinForecastModel

class BitcoinForecastApp:
    def __init__(self):
        # Load configuration
        with open('/app/configs/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, self.config['app']['log_level']),
            format=self.config['app']['log_format'],
            datefmt=self.config['app']['log_date_format']
        )
        self.logger = logging.getLogger(__name__)
        
        # Load data paths
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
        
        # Initialize Kafka consumer with config settings
        self.consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            **self.config['kafka']['consumer']
        )
        
        # Initialize the TensorFlow Probability model
        self.model = BitcoinForecastModel()
        
        # Initialize last prediction time
        self.last_prediction_time = None
        
        # Set window size for historical data from config
        self.window_size = timedelta(seconds=self.config['model']['instant']['window_size'])
        
        self.logger.info(f"Initialized {self.config['app']['name']} v{self.config['app']['version']}")
        self.logger.info(f"Data file: {self.data_file}")
        self.logger.info(f"Predictions file: {self.predictions_file}")
        self.logger.info(f"Metrics file: {self.metrics_file}")
        self.logger.info(f"Kafka bootstrap servers: {self.kafka_bootstrap_servers}")
        self.logger.info(f"Kafka topic: {self.kafka_topic}")

    def format_timestamp(self, dt):
        """
        Unified function to format timestamps to seconds precision.
        Args:
            dt: datetime object or timestamp string
        Returns:
            str: Formatted timestamp string in ISO8601 format with seconds precision
        """
        if isinstance(dt, str):
            dt = pd.to_datetime(dt)
        elif isinstance(dt, (int, float)):
            dt = datetime.fromtimestamp(dt)
        
        # Round to seconds by truncating microseconds
        dt = dt.replace(microsecond=0)
        return dt.strftime(self.config['data_format']['timestamp']['format'])

    def load_historical_data(self):
        """Load historical data from CSV file with windowing."""
        try:
            # Read only the last window_size of data
            df = pd.read_csv(
                self.data_file,
                names=self.config['data_format']['columns']['raw_data']['names'],
                skiprows=1  # Skip header row
            )
            
            # Convert timestamp to datetime and round to seconds
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.floor('S')
            
            # Filter to last window_size
            cutoff_time = datetime.now().replace(microsecond=0) - self.window_size
            df = df[df['timestamp'] >= cutoff_time]
            
            # Ensure numeric columns are float64
            numeric_columns = self.config['data_format']['columns']['raw_data']['names'][1:]  # Skip timestamp
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            return df
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            return pd.DataFrame()

    def save_prediction(self, prediction_time, actual_price, predicted_price, confidence_interval):
        """Save prediction to CSV file with actual prediction timestamp."""
        try:
            # Format timestamp using unified function
            formatted_timestamp = self.format_timestamp(prediction_time)
            
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
            
            self.logger.info(f"Saved prediction for {formatted_timestamp}")
        except Exception as e:
            self.logger.error(f"Error saving prediction: {str(e)}")
            raise

    def save_metrics(self, prediction_time, mae, rmse, mape):
        """Save prediction metrics to CSV file with actual prediction timestamp."""
        try:
            # Format timestamp using unified function
            formatted_timestamp = self.format_timestamp(prediction_time)
            
            metrics_data = {
                'timestamp': formatted_timestamp,
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
            
            self.logger.info(f"Saved metrics for {formatted_timestamp}")
            
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")

    def make_prediction(self, message_time, actual_price):
        """Make a prediction for the current timestamp."""
        try:
            # Get historical data for model input
            historical_data = self.load_historical_data()
            if not historical_data.empty:
                # Convert to numpy array for model input
                price_series = historical_data['close'].values
                
                # Only update model if we have new data
                if self.last_prediction_time is None or \
                   (message_time - self.last_prediction_time).total_seconds() >= self.config['model']['instant']['update_interval']:
                    self.model.update(price_series)
                    self.last_prediction_time = message_time
                
                # Generate forecast
                predicted_price, lower_bound, upper_bound = self.model.forecast()
                confidence_interval = (lower_bound, upper_bound)
                
                # Calculate metrics
                mae = abs(predicted_price - actual_price)
                rmse = np.sqrt(mae ** 2)
                mape = abs((predicted_price - actual_price) / actual_price) * 100
                
                # Get the actual prediction time and round to seconds
                prediction_time = datetime.now().replace(microsecond=0)
                
                # Log the prediction with the actual prediction timestamp
                self.logger.info(f"Made prediction at {self.format_timestamp(prediction_time)}: Actual={actual_price:.2f}, Predicted={predicted_price:.2f}")
                
                # Save prediction and metrics with actual prediction timestamp
                self.save_prediction(prediction_time, actual_price, predicted_price, confidence_interval)
                self.save_metrics(prediction_time, mae, rmse, mape)
                
                # Clean up memory
                del historical_data
                gc.collect()
                
                return True
            else:
                self.logger.warning("No historical data available for prediction")
                return False
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return False

    def process_new_data(self, message):
        """Process new data from Kafka."""
        try:
            data = message.value
            # Round message timestamp to seconds
            message_time = pd.to_datetime(data['timestamp']).floor('S')
            actual_price = float(data['close'])
            
            # Make prediction using message time for model update but actual time for prediction
            self.make_prediction(message_time, actual_price)
            
        except Exception as e:
            self.logger.error(f"Error processing new data: {e}")

    def run(self):
        """Run the Bitcoin price forecasting application."""
        self.logger.info("Starting Bitcoin price forecasting...")
        
        try:
            while True:
                # Poll for new messages
                messages = self.consumer.poll(
                    timeout_ms=int(self.config['memory']['cleanup_interval'] * 1000),
                    max_records=self.config['kafka']['consumer']['max_poll_records']
                )
                
                for tp, msgs in messages.items():
                    for message in msgs:
                        self.process_new_data(message)
                
                # Clean up memory periodically
                gc.collect()
                
                # Small sleep to prevent CPU overuse
                time.sleep(self.config['memory']['sleep_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    app = BitcoinForecastApp()
    app.run() 