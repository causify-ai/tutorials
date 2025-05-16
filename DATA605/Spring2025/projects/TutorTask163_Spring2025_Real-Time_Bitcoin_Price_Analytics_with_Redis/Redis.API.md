<!-- toc -->

- [Redis API for Bitcoin Price Analytics](#redis-api-for-bitcoin-price-analytics)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [Native Redis API](#native-redis-api)
    + [Connection Management](#connection-management)
    + [Data Structures](#data-structures)
    + [Pub/Sub Messaging](#pub-sub-messaging)
    + [Time Series Operations](#time-series-operations)
  * [Bitcoin Analytics Wrapper Layer](#bitcoin-analytics-wrapper-layer)
    + [Connection Management](#connection-management-1)
    + [Data Fetching](#data-fetching)
    + [Data Storage](#data-storage)
    + [Data Retrieval](#data-retrieval)
    + [Time Series Analysis](#time-series-analysis)
    + [Real-time Updates](#real-time-updates)
    + [Price Alerting System](#price-alerting-system)
    + [Visualization](#visualization)
  * [Usage Examples](#usage-examples)
    + [Basic Operations](#basic-operations)
    + [Advanced Analytics](#advanced-analytics)
    + [Real-time Monitoring](#real-time-monitoring)

<!-- tocstop -->

# Redis API for Bitcoin Price Analytics

This document provides a comprehensive guide to the Redis API used in the Real-time Bitcoin Price Analytics project. It covers both the native Redis commands and the custom wrapper layer created to simplify Bitcoin price data management, analysis, and visualization.

## Table of Contents

The documentation is organized into three main sections:
1. Native Redis API - Core Redis functionality used in the project
2. Bitcoin Analytics Wrapper Layer - Custom functions built on top of Redis
3. Usage Examples - Practical examples demonstrating the API in action

### Hierarchy

Hierarchy of the markdown file follows this structure:
```
# Level 1 (Main title - Redis API for Bitcoin Price Analytics)
## Level 2 (Main sections)
### Level 3 (Subsections)
```

## Native Redis API

This section covers the fundamental Redis functionality leveraged in our Bitcoin analytics system.

### Connection Management

Redis provides simple connection mechanisms that allow applications to establish communication with Redis servers:

```python
# Native Redis connection
import redis
r = redis.Redis(
    host='hostname',
    port=6379,
    password='password',
    decode_responses=True  # Automatically decode byte responses to strings
)

# Connection verification
ping_response = r.ping()  # Returns True if connection is alive
```

### Data Structures

Redis offers multiple data structures that are used in this project:

1. **Strings**: Simple key-value pairs
   ```python
   # Set and get a string value
   r.set("bitcoin:current_price:usd", 45000.25)
   price = float(r.get("bitcoin:current_price:usd"))
   ```

2. **Hashes**: Maps between string fields and values
   ```python
   # Store complete data point as a hash
   r.hset("bitcoin:data:usd", mapping={
       'price': 45000.25,
       'market_cap': 850000000000,
       'volume_24h': 24000000000,
       'change_24h': 2.5,
       'timestamp': 1651234567
   })
   
   # Get all hash fields
   bitcoin_data = r.hgetall("bitcoin:data:usd")
   ```

3. **Sorted Sets**: Sets of unique elements ordered by score
   ```python
   # Add to time series (using sorted set with timestamp as score)
   r.zadd("bitcoin:price_history:usd", {json.dumps(data_point): timestamp})
   
   # Get items by score range (timestamps in this case)
   history = r.zrangebyscore("bitcoin:price_history:usd", start_time, end_time)
   ```

### Pub/Sub Messaging

Redis provides publish/subscribe messaging for real-time applications:

```python
# Create a subscriber
pubsub = r.pubsub()
pubsub.subscribe('bitcoin_price_updates')

# Publish a message
r.publish('bitcoin_price_updates', json.dumps({'usd': 45000.25, 'timestamp': 1651234567}))

# Receive messages
message = pubsub.get_message()
if message and message['type'] == 'message':
    data = json.loads(message['data'])
```

### Time Series Operations

Redis can be used for time series data with sorted sets:

```python
# Add time series data point with timestamp as score
r.zadd('bitcoin:price:history:usd', {str(timestamp): price})

# Retrieve data points within a time range
data_points = r.zrangebyscore('bitcoin:price:history:usd', min_timestamp, max_timestamp, withscores=True)
```

## Bitcoin Analytics Wrapper Layer

Our wrapper layer provides a simplified interface for Bitcoin price analytics, abstracting the complexity of Redis operations.

### Connection Management

```python
def connect_to_redis(host=None, port=None, password=None):
    """
    Connect to Redis server with error handling and defaults from environment variables.
    """
    # Implementation details...
    return redis_connection

def verify_redis_connection(redis_conn=None, host=None, port=None, password=None):
    """
    Verify connection to Redis server and display connection details.
    """
    # Implementation details...
    return connection_success
```

### Data Fetching

```python
def fetch_bitcoin_price(currency='usd'):
    """
    Fetch current Bitcoin price from CoinGecko API.
    """
    # Implementation details...
    return price_data

def fetch_bitcoin_historical(days=1, currency='usd'):
    """
    Fetch historical Bitcoin price data from CoinGecko API.
    """
    # Implementation details...
    return historical_data
```

### Data Storage

```python
def store_bitcoin_price(redis_conn, price_data, currency='usd'):
    """
    Store Bitcoin price data in Redis using strings, hashes, and sorted sets.
    """
    # Implementation details...
    return success

def store_historical_price(redis_conn, price_data, currency='usd'):
    """
    Store historical Bitcoin price data in Redis.
    """
    # Implementation details...
    return success
```

### Data Retrieval

```python
def get_current_bitcoin_price(redis_conn, currency='usd'):
    """
    Get current Bitcoin price from Redis.
    """
    # Implementation details...
    return price

def get_bitcoin_data(redis_conn, currency='usd'):
    """
    Get all Bitcoin data from Redis including price, market cap, etc.
    """
    # Implementation details...
    return data

def get_price_history(redis_conn, start_time=None, end_time=None, currency='usd'):
    """
    Get Bitcoin price history from Redis within a specific time range.
    """
    # Implementation details...
    return history
```

### Time Series Analysis

```python
def get_price_dataframe(price_history, currency='usd'):
    """
    Convert price history list to a Pandas DataFrame.
    """
    # Implementation details...
    return dataframe

def calculate_moving_average(df, window=10, column='price'):
    """
    Calculate moving average of a column in the DataFrame.
    """
    # Implementation details...
    return moving_average

def calculate_percent_change(df, periods=1, column='price'):
    """
    Calculate percent change over a number of periods.
    """
    # Implementation details...
    return percent_change

def detect_price_anomalies(df, threshold=2.0, column='price'):
    """
    Detect anomalies in price data using Z-score method.
    """
    # Implementation details...
    return anomalies
```

### Real-time Updates

```python
def publish_price_update(redis_conn, price_data, channel='bitcoin_price_updates'):
    """
    Publish Bitcoin price update to a Redis channel.
    """
    # Implementation details...
    return num_receivers

def create_subscriber(redis_conn, channel='bitcoin_price_updates'):
    """
    Create a Redis subscriber for a channel.
    """
    # Implementation details...
    return pubsub

def monitor_price_updates(pubsub, duration=3600):
    """
    Monitor price updates for a specified duration.
    """
    # Implementation details...
```

### Price Alerting System

```python
class BitcoinPriceAlertSystem:
    """
    Real-time Bitcoin price alert system using Redis Pub/Sub.
    Monitors price updates and triggers alerts based on thresholds.
    """
    
    def __init__(self, redis_conn):
        # Initialize alert system
        
    def add_threshold_alert(self, threshold, is_upper=True, message=None):
        """Add a price threshold alert."""
        
    def add_percent_change_alert(self, percent, period_minutes=5, message=None):
        """Add a percent change alert."""
        
    def start_monitoring(self):
        """Start monitoring Bitcoin price updates."""
        
    def stop_monitoring(self):
        """Stop monitoring Bitcoin price updates."""
```

### Visualization

```python
def prepare_price_plot_data(df):
    """
    Prepare Bitcoin price data for plotting.
    """
    # Implementation details...
    return timestamps, prices, moving_avg_10, moving_avg_30

def plot_price_data(df, output_file):
    """
    Plot price data and save to file.
    """
    # Implementation details...
    return fig
```

## Usage Examples

This section demonstrates how to use the API for various Bitcoin analytics tasks.

### Basic Operations

```python
# Connect to Redis
redis_conn = connect_to_redis(host, port, password)

# Fetch and store current Bitcoin price
bitcoin_data = fetch_bitcoin_price(currency='usd')
success = store_bitcoin_price(redis_conn, bitcoin_data)

# Retrieve stored current price
price = get_current_bitcoin_price(redis_conn)
print(f"Current Bitcoin price: ${price:,.2f}")
```

### Advanced Analytics

```python
# Get price history from Redis
end_time = int(time.time())
start_time = end_time - (24 * 3600)  # 24 hours ago
price_history = get_price_history(redis_conn, start_time, end_time)

# Convert to DataFrame for analysis
df = get_price_dataframe(price_history)

# Calculate moving averages
df['ma_10'] = calculate_moving_average(df, window=10)
df['ma_30'] = calculate_moving_average(df, window=30)

# Detect anomalies
anomalies = detect_price_anomalies(df, threshold=2.0)

# Visualize the data
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df.index, df['price'], label='Price', color='blue')
ax.plot(df.index, df['ma_10'], label='10-point MA', color='red')
ax.plot(df.index, df['ma_30'], label='30-point MA', color='green')
plt.legend()
plt.show()
```

### Real-time Monitoring

```python
# Create a subscription to the Bitcoin price updates channel
pubsub = create_subscriber(redis_conn, channel='bitcoin_price_updates')

# Set up price alerts
alert_system = BitcoinPriceAlertSystem(redis_conn)
alert_system.add_threshold_alert(50000, is_upper=True)  # Alert when price exceeds $50,000
alert_system.add_threshold_alert(40000, is_upper=False)  # Alert when price falls below $40,000
alert_system.add_percent_change_alert(2.0, period_minutes=5)  # Alert on 2% change within 5 minutes

# Start monitoring
alert_system.start_monitoring()

# In a separate process/thread: Publish updates
bitcoin_data = fetch_bitcoin_price()
publish_price_update(redis_conn, bitcoin_data)
```
