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
with open('/app/configs/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

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
        # Load historical data
        historical_data = pd.read_csv(config['data']['raw_data']['historical_data']['file'])
        logger.info(f"Initialized model with {len(historical_data)} historical records")
        
        # Initialize and train model (simplified for example)
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(60, 1)),
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dense(1)
        ])
        
        # Compile and train model (simplified)
        model.compile(optimizer='adam', loss='mse')
        # Add actual training code here
        
        return model
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise

# Make prediction
def make_prediction(model, data):
    try:
        # Prepare data for prediction
        # Add actual prediction logic here
        predicted_price = 95000.0  # Placeholder
        confidence_interval = (predicted_price - 100, predicted_price + 100)  # Placeholder
        
        return predicted_price, confidence_interval
    except Exception as e:
        logger.error(f"Failed to make prediction: {e}")
        raise

# Save prediction
def save_prediction(timestamp, actual_price, predicted_price, confidence_interval):
    try:
        # Save prediction
        prediction = {
            'timestamp': timestamp,
            'actual_price': actual_price,
            'predicted_price': predicted_price,
            'lower_bound': confidence_interval[0],
            'upper_bound': confidence_interval[1]
        }
        
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        os.makedirs(os.path.dirname(predictions_file), exist_ok=True)
        
        df = pd.DataFrame([prediction])
        if os.path.exists(predictions_file):
            df.to_csv(predictions_file, mode='a', header=False, index=False)
        else:
            df.to_csv(predictions_file, index=False)
            
        logger.info(f"Saved prediction for {timestamp}")
        
        # Save metrics
        metrics = {
            'timestamp': timestamp,
            'actual_price': actual_price,
            'predicted_price': predicted_price,
            'error': abs(actual_price - predicted_price),
            'error_percentage': abs(actual_price - predicted_price) / actual_price * 100
        }
        
        metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
        
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
                # Get current timestamp
                current_time = datetime.now()
                
                # Consume message from Kafka
                message = next(consumer)
                data = message.value
                
                # Make prediction
                predicted_price, confidence_interval = make_prediction(model, data)
                
                # Save prediction with current timestamp
                save_prediction(
                    current_time,
                    data['price'],
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