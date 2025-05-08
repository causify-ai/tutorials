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
import tensorflow as tf
import tensorflow_probability as tfp
from kafka import KafkaConsumer
from kafka.errors import KafkaError

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
    config = {
        'kafka': {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
            'topic': os.getenv('KAFKA_TOPIC', 'bitcoin-prices'),
            'group_id': 'bitcoin-forecast'
        },
        'data': {
            'predictions': {
                'instant_data': {
                    'predictions_file': 'data/predictions/instant_predictions.csv',
                    'metrics_file': 'data/predictions/instant_metrics.csv'
                }
            }
        }
    }
    logger.warning("Using default configuration")

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

# Initialize model
def init_model():
    try:
        # Create a simple model that doesn't require historical data
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(32, activation='relu', input_shape=(1,)),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        
        # Compile model
        model.compile(optimizer='adam', loss='mse')
        logger.info("Initialized simple forecasting model")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise

# Make prediction
def make_prediction(model, data):
    try:
        # Get the current price
        current_price = float(data['price'])
        
        # Make a simple prediction (placeholder)
        # In a real implementation, this would use the model to make predictions
        predicted_price = current_price * 1.001  # Simple 0.1% increase
        confidence_interval = (predicted_price * 0.99, predicted_price * 1.01)  # ±1% confidence interval
        
        return predicted_price, confidence_interval
    except Exception as e:
        logger.error(f"Failed to make prediction: {e}")
        raise

# Save prediction
def save_prediction(timestamp, actual_price, predicted_price, confidence_interval):
    try:
        # Ensure directory exists
        predictions_dir = os.path.dirname(config['data']['predictions']['instant_data']['predictions_file'])
        metrics_dir = os.path.dirname(config['data']['predictions']['instant_data']['metrics_file'])
        os.makedirs(predictions_dir, exist_ok=True)
        os.makedirs(metrics_dir, exist_ok=True)
        
        # Save prediction
        prediction = {
            'timestamp': timestamp,
            'actual_price': actual_price,
            'predicted_price': predicted_price,
            'lower_bound': confidence_interval[0],
            'upper_bound': confidence_interval[1]
        }
        
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        df = pd.DataFrame([prediction])
        if os.path.exists(predictions_file):
            df.to_csv(predictions_file, mode='a', header=False, index=False)
        else:
            df.to_csv(predictions_file, index=False)
            
        logger.info(f"Saved prediction for {timestamp}")
        
        # Calculate and save metrics
        error = abs(actual_price - predicted_price)
        error_percentage = (error / actual_price) * 100
        
        metrics = {
            'timestamp': timestamp,
            'mae': error,
            'rmse': error,  # Simplified for now
            'mape': error_percentage
        }
        
        metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        df_metrics = pd.DataFrame([metrics])
        if os.path.exists(metrics_file):
            df_metrics.to_csv(metrics_file, mode='a', header=False, index=False)
        else:
            df_metrics.to_csv(metrics_file, index=False)
            
        logger.info(f"Saved metrics for {timestamp}")
        logger.info(f"Made prediction for {timestamp}: Actual={actual_price:.2f}, Predicted={predicted_price:.2f}")
        
    except Exception as e:
        logger.error(f"Failed to save prediction: {e}")
        raise

def main():
    logger.info("Starting Bitcoin price forecasting...")
    
    # Initialize components
    consumer = init_kafka_consumer()
    model = init_model()
    
    try:
        while True:
            try:
                # Consume message from Kafka
                message = next(consumer)
                data = message.value
                
                # Get timestamp from data or use current time
                timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                
                # Make prediction
                predicted_price, confidence_interval = make_prediction(model, data)
                
                # Save prediction with original timestamp
                save_prediction(
                    timestamp,
                    float(data['price']),
                    predicted_price,
                    confidence_interval
                )
                
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