import pandas as pd
import os
from utilities.logger import get_logger
import json
from datetime import datetime, timezone
import time
import yaml
import csv
import asyncio
import websockets
import numpy as np
from utilities.price_format import normalize_price
from utilities.timestamp_format import to_iso8601, format_timestamp
from utilities.unified_config import get_service_config
from kafka import KafkaProducer
import traceback
import statistics

# Get service name from environment or use default
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'data_collector')

# Load config using unified config parser
config = get_service_config(SERVICE_NAME)

# Configure logging
logger = get_logger(__name__, log_level=config['app']['log_level'])
logger.info(f"Starting {SERVICE_NAME} service with unified configuration")

# Get timestamp format from config
TIMESTAMP_FORMAT = config['data_format']['timestamp']['format']

# Add robust timestamp conversion
def safe_iso8601(ts):
    # If ts is a float/int, treat as epoch
    if isinstance(ts, (int, float)):
        # Validate reasonable range (2000-01-01 to 2100-01-01)
        if ts < 946684800 or ts > 4102444800:
            raise ValueError(f"Timestamp {ts} out of range")
        return format_timestamp(ts, use_t_separator=True)
    # If already string, try to parse and reformat
    try:
        dt = pd.to_datetime(ts, utc=True)
        return format_timestamp(dt, use_t_separator=True)
    except Exception:
        raise ValueError(f"Unrecognized timestamp: {ts}")

# Enhanced data validation for cryptocurrency prices
def validate_bitcoin_price(price):
    """
    Validate Bitcoin price is within reasonable range
    Returns: (is_valid, message)
    """
    if not isinstance(price, (int, float)):
        return False, f"Price must be numeric, got {type(price)}"
    
    # Bitcoin should be within reasonable range (100 - 200,000 USD)
    if price < 100 or price > 200000:
        return False, f"Bitcoin price {price} outside reasonable range (100-200000)"
        
    return True, "Price validated"

# Data quality check function
def check_data_quality(data_point, recent_prices=None):
    """
    Check for data quality issues such as:
    - Missing required fields
    - Invalid values
    - Outliers compared to recent prices
    """
    # Required fields
    required_fields = ['timestamp', 'close']
    for field in required_fields:
        if field not in data_point or data_point[field] is None:
            return False, f"Missing required field: {field}"
    
    # Timestamp validation
    try:
        if isinstance(data_point['timestamp'], str):
            pd.to_datetime(data_point['timestamp'])
    except:
        return False, f"Invalid timestamp: {data_point['timestamp']}"
    
    # Price validation
    price_valid, price_msg = validate_bitcoin_price(data_point['close'])
    if not price_valid:
        return False, price_msg
    
    # Outlier detection when we have recent prices
    if recent_prices and len(recent_prices) >= 5:
        current_price = data_point['close']
        
        # Method 1: Median Absolute Deviation (robust to outliers)
        median_price = statistics.median(recent_prices)
        deviations = [abs(p - median_price) for p in recent_prices]
        mad = statistics.median(deviations)
        
        # Modified z-score
        if mad > 0:  # Avoid division by zero
            modified_z = 0.6745 * abs(current_price - median_price) / mad
            if modified_z > 10:  # Very extreme outlier
                return False, f"Extreme price outlier detected: {current_price} (z-score: {modified_z:.2f})"
            elif modified_z > 5:  # Significant outlier, but still possible in crypto
                logger.warning(f"Potential price outlier: {current_price} (z-score: {modified_z:.2f})")
        
        # Method 2: Percentage change
        pct_change = abs(current_price - recent_prices[-1]) / recent_prices[-1]
        if pct_change > 0.20:  # 20% price jump in 1 second is suspicious
            return False, f"Suspicious price jump: {pct_change:.2%} ({recent_prices[-1]} → {current_price})"
        elif pct_change > 0.10:  # 10% jump is unusual but possible
            logger.warning(f"Large price movement detected: {pct_change:.2%} ({recent_prices[-1]} → {current_price})")
        
    return True, "Data validated"

# Robust save_data function with enhanced validation
def save_data(data, file_path, recent_prices=None):
    try:
        # Data quality checks
        quality_ok, quality_msg = check_data_quality(data, recent_prices)
        if not quality_ok:
            logger.warning(f"Skipping low quality data: {quality_msg}")
            return False
            
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data:
                data[col] = data.get('price', 0)
        
        # Use robust timestamp conversion
        data['timestamp'] = safe_iso8601(data['timestamp'])
        
        # Create DataFrame and ensure correct data types
        df = pd.DataFrame([data], columns=required_columns)
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Check for NaN values after conversion
        if df.isna().any().any():
            logger.warning(f"NaN values detected after conversion: {df.to_dict('records')[0]}")
            # Fill NaN with reasonable values
            if df['close'].isna().any():
                return False  # Skip record if close price is NaN
            # Fill other NaNs with close price
            for col in ['open', 'high', 'low']:
                if df[col].isna().any():
                    df[col] = df['close']
            # Fill volume with 0
            if df['volume'].isna().any():
                df['volume'] = 0
        
        # Save to file with file locking
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a' if os.path.exists(file_path) else 'w') as f:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                if f.tell() == 0:
                    df.to_csv(f, index=False)
                else:
                    df.to_csv(f, mode='a', header=False, index=False)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
                
        logger.info(f"Saved data to {file_path}: timestamp={data['timestamp']}, close={data['close']}")
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}\n{traceback.format_exc()}")
        return False

class BitcoinDataCollector:
    def __init__(self, config):
        self.config = config
        self.recent_prices = []  # Keep track of recent prices for outlier detection
        self.max_recent_prices = 100  # Store up to 100 recent prices
        
        # Initialize Kafka producer with retries and acknowledgments
        self.producer = KafkaProducer(
            bootstrap_servers=config['kafka']['bootstrap_servers'],
            value_serializer=lambda x: json.dumps(x).encode(),
            acks='all',  # Wait for all replicas to acknowledge
            retries=5,   # Retry failed sends
            retry_backoff_ms=500  # Backoff between retries
        )
        
        self.data_file = config['data']['raw_data']['instant_data']['file']
        logger.info(f"Data will be saved to {self.data_file}")
        
        # Initialize stats tracking
        self.stats = {
            "total_records": 0,
            "valid_records": 0,
            "kafka_errors": 0,
            "last_price": None,
            "start_time": datetime.now(timezone.utc)
        }
        
        # Set up stat reporting interval (but don't create task yet)
        self.report_interval = config.get('report_interval', 300)  # Default 5 minutes
        # We'll start the periodic report task in the stream method where we have an event loop

    def publish_to_kafka(self, bar, ts):
        try:
            self.producer.send(self.config['kafka']['topic'], bar)
            self.producer.flush()
            logger.info(f"[System Time: {datetime.now().strftime(TIMESTAMP_FORMAT)}] [Data Time: {ts}] → pushed to Kafka: {bar}")
            return True
        except Exception as e:
            logger.error(f"Kafka error: {e}")
            self.stats["kafka_errors"] += 1
            return False
    
    def update_recent_prices(self, price):
        """Update list of recent prices for outlier detection"""
        self.recent_prices.append(price)
        if len(self.recent_prices) > self.max_recent_prices:
            self.recent_prices.pop(0)  # Remove oldest price
        self.stats["last_price"] = price
    
    async def periodic_stats_report(self):
        """Report statistics periodically"""
        while True:
            await asyncio.sleep(self.report_interval)
            runtime = datetime.now(timezone.utc) - self.stats["start_time"]
            hours = runtime.total_seconds() / 3600
            
            if self.stats["total_records"] > 0:
                valid_pct = (self.stats["valid_records"] / self.stats["total_records"]) * 100
            else:
                valid_pct = 0
                
            logger.info(
                f"STATS: Runtime: {runtime}, "
                f"Records: {self.stats['total_records']} total, "
                f"{self.stats['valid_records']} valid ({valid_pct:.1f}%), "
                f"Kafka errors: {self.stats['kafka_errors']}, "
                f"Records/hour: {self.stats['valid_records']/max(1,hours):.1f}, "
                f"Last price: {self.stats['last_price']}"
            )

    async def stream_1s_ohlc(self):
        uri = "wss://ws-feed.exchange.coinbase.com"
        curr_sec = None
        o = h = l = c = v = None
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        # Start the stats reporting task now that we're in an async context
        stats_task = asyncio.create_task(self.periodic_stats_report())
        logger.info("Started periodic stats reporting task")
        
        try:
            while True:
                try:
                    async with websockets.connect(uri, ping_interval=20) as ws:
                        logger.info("Connected to Coinbase WebSocket")
                        subscribe_msg = {
                            "type": "subscribe",
                            "channels": [{"name": "ticker", "product_ids": ["BTC-USD"]}]
                        }
                        await ws.send(json.dumps(subscribe_msg))
                        consecutive_errors = 0  # Reset error counter on successful connection
                        
                        async for message in ws:
                            try:
                                msg = json.loads(message)
                                if msg.get("type") != "ticker":
                                    continue
                                    
                                ts = datetime.fromisoformat(msg["time"].replace("Z", "+00:00"))
                                price = float(msg["price"])
                                size = float(msg.get("last_size", 0.0))
                                
                                # Basic validation of price and size
                                if price <= 0 or size < 0:
                                    logger.warning(f"Invalid price or size: price={price}, size={size}")
                                    continue
                                    
                                sec = int(ts.timestamp())
                                
                                if curr_sec is None:
                                    curr_sec = sec
                                    o = h = l = c = price
                                    v = size
                                elif sec == curr_sec:
                                    h = max(h, price)
                                    l = min(l, price)
                                    c = price
                                    v += size
                                else:
                                    # Flush the completed second to CSV and Kafka
                                    self.stats["total_records"] += 1
                                    
                                    try:
                                        row_ts = safe_iso8601(curr_sec)
                                    except Exception as e:
                                        logger.error(f"Skipping row due to bad timestamp: {curr_sec} ({e})")
                                        curr_sec = sec
                                        o = h = l = c = price
                                        v = size
                                        continue
                                        
                                    bar = {
                                        'timestamp': row_ts,
                                        'open': normalize_price(o),
                                        'high': normalize_price(h),
                                        'low': normalize_price(l),
                                        'close': normalize_price(c),
                                        'volume': v
                                    }
                                    
                                    # Update recent prices list before validation
                                    self.update_recent_prices(normalize_price(c))
                                    
                                    # Save data and publish to Kafka if valid
                                    if save_data(bar, self.data_file, self.recent_prices):
                                        self.publish_to_kafka(bar=bar, ts=row_ts)
                                        self.stats["valid_records"] += 1
                                    
                                    # Start a new bar
                                    curr_sec = sec
                                    o = h = l = c = price
                                    v = size
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON message: {message[:100]}...")
                            except Exception as e:
                                logger.error(f"Error processing message: {e}\n{traceback.format_exc()}")
            
                except (websockets.ConnectionClosed, asyncio.TimeoutError) as e:
                    consecutive_errors += 1
                    backoff = min(30, 5 * consecutive_errors)  # Exponential backoff, max 30 seconds
                    logger.warning(f"WebSocket disconnected: {e}. Reconnecting in {backoff}s… (attempt {consecutive_errors})")
                    await asyncio.sleep(backoff)
                    
                except Exception as e:
                    consecutive_errors += 1
                    backoff = min(60, 5 * consecutive_errors)  # Longer backoff for unexpected errors
                    logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}. Restarting in {backoff}s… (attempt {consecutive_errors})")
                    await asyncio.sleep(backoff)
                    
                # Give up after too many consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(f"Too many consecutive errors ({consecutive_errors}). Exiting and waiting for container restart.")
                    return  # Exit the function, container orchestration will restart
        finally:
            # Clean up the stats task if we're exiting
            if not stats_task.done():
                stats_task.cancel()
                try:
                    await stats_task
                except asyncio.CancelledError:
                    pass

def main():
    logger.info(f"Starting real-time Coinbase OHLCV collector for BTC-USD")
    collector = BitcoinDataCollector(config)
    asyncio.run(collector.stream_1s_ohlc())

if __name__ == "__main__":
    main() 