import pandas as pd
import os
import logging
import json
from datetime import datetime
from kafka import KafkaProducer
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def init_kafka_producer():
    """Initialize Kafka producer."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        logger.info(f"Initialized Kafka producer with bootstrap servers: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')}")
        return producer
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        raise

def save_data(data, file_path):
    """Save data to CSV file with proper timestamp format and column names."""
    try:
        # Ensure data has all required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        # If timestamp is not in ISO format, convert it
        if 'timestamp' in data:
            try:
                # Try to parse the timestamp
                ts = pd.Timestamp(data['timestamp'])
                # Convert to ISO format
                data['timestamp'] = ts.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                # If parsing fails, use current time
                data['timestamp'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        else:
            data['timestamp'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        # Ensure all required columns exist
        for col in required_columns:
            if col not in data:
                if col == 'timestamp':
                    continue
                data[col] = data.get('price', 0)  # Use price for all columns if not available
        
        # Create DataFrame with proper column order
        df = pd.DataFrame([data], columns=required_columns)
        
        # Ensure numeric columns are float64
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write to file with proper locking
        with open(file_path, 'a' if os.path.exists(file_path) else 'w') as f:
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
        
        logger.info(f"Saved data to {file_path}")
        return df
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise

def main():
    """Main function to collect and save Bitcoin price data."""
    try:
        # Initialize Kafka producer
        producer = init_kafka_producer()
        
        # Get configuration
        topic = os.getenv('KAFKA_TOPIC', 'bitcoin-prices')
        data_file = os.path.join('/app/data', 'raw/instant_data.csv')
        
        logger.info(f"Starting data collection for topic: {topic}")
        logger.info(f"Data will be saved to: {data_file}")
        
        while True:
            try:
                # Get current timestamp
                current_time = datetime.now()
                timestamp = current_time.strftime('%Y-%m-%dT%H:%M:%S')
                
                # Simulate getting Bitcoin price (replace with actual API call)
                price = 95000.0  # Placeholder
                
                # Create data point
                data = {
                    'timestamp': timestamp,
                    'price': price,
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price,
                    'volume': 0.0
                }
                
                # Save to file
                save_data(data, data_file)
                
                # Send to Kafka
                producer.send(topic, value=data)
                producer.flush()
                
                logger.info(f"Collected and sent data for {timestamp}")
                
                # Wait for next collection
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if 'producer' in locals():
            producer.close()

if __name__ == "__main__":
    main() 