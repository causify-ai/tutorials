<!-- toc -->

- [Real-time Bitcoin Price Analytics with Redis](#real-time-bitcoin-price-analytics-with-redis)
  * [Project Overview](#project-overview)
  * [Architecture](#architecture)
    + [Data Flow](#data-flow)
    + [Component Breakdown](#component-breakdown)
  * [Implementation](#implementation)
    + [Core Functionality](#core-functionality)
    + [Time Series Analysis](#time-series-analysis)
    + [Real-time Alerting](#real-time-alerting)
  * [Demonstration](#demonstration)
    + [Data Collection](#data-collection)
    + [Analytics Dashboard](#analytics-dashboard)
    + [Alert Monitoring](#alert-monitoring)
  * [Conclusions](#conclusions)

<!-- tocstop -->

# Real-time Bitcoin Price Analytics with Redis

This project implements a complete system for fetching, storing, analyzing, and visualizing Bitcoin price data in real-time. It leverages Redis as the primary data store and message broker, with Python-based analytics and visualization.

## Project Overview

The Bitcoin price analytics platform collects price data from the CoinGecko API and uses Redis to create a robust real-time analytics system. The project demonstrates:

1. **High-performance data persistence** using Redis data structures
2. **Real-time messaging** with Redis Pub/Sub
3. **Time series analytics** for cryptocurrency price tracking
4. **Anomaly detection** for identifying unusual price movements
5. **Price alerting system** for threshold and percent-change notifications

The system is designed to be extensible, allowing for additional data sources and more sophisticated analytics to be added over time.

## Architecture

The system is built on a layered architecture that separates concerns and enables scalability.

### Data Flow

The data flows through the system in the following sequence:

1. **Data Collection Layer**
   - CoinGecko API integration fetches current and historical Bitcoin prices
   - Data normalization and transformation prepare the data for storage
   - Regular polling ensures up-to-date information

2. **Storage Layer**
   - Redis strings store the current Bitcoin price for fast access
   - Redis hashes maintain complete data points with metadata
   - Redis sorted sets create time series data structures with timestamps as scores

3. **Processing Layer**
   - Time series analysis computes moving averages, volatility measures, and trends
   - Anomaly detection identifies unusual price movements
   - Data conversion transforms Redis structures into Pandas DataFrames for analysis

4. **Communication Layer**
   - Redis Pub/Sub channels distribute real-time price updates
   - Subscriber components consume and process update messages
   - Alert engine monitors prices and notifies on threshold breaches

5. **Visualization Layer**
   - Time series plots show Bitcoin price trends with moving averages
   - Volatility indicators highlight market stability
   - Anomaly markers identify potential trading opportunities

### Component Breakdown

The system consists of several key components:

- **Redis_utils.py**: Core utility library with Redis operations, data fetching, and analytics
- **Redis.API.ipynb**: Documentation and demonstration of the API capabilities
- **Redis.example.ipynb**: End-to-end implementation showing practical usage

## Implementation

The implementation focuses on creating a highly responsive system that can handle real-time data while providing sophisticated analytics.

### Core Functionality

The project implements several core features:

```python
# Fetch current Bitcoin price
bitcoin_data = fetch_bitcoin_price(currency='usd')
print(f"Current Bitcoin price: ${bitcoin_data['usd']:,.2f}")

# Store data in Redis
success = store_bitcoin_price(redis_conn, bitcoin_data)

# Fetch historical data
historical_data = fetch_bitcoin_historical(days=7)

# Process and store historical data
def process_historical_data(historical_data):
    for timestamp_ms, price in historical_data['prices']:
        timestamp = int(timestamp_ms/1000)
        data_point = {
            'usd': price,
            'timestamp': timestamp,
            # Additional fields...
        }
        store_historical_price(redis_conn, data_point)
```

Each historical data point is stored with complete metadata, enabling rich analytics and visualizations.

### Time Series Analysis

The system implements several time series analysis techniques:

```python
# Get price history from Redis
price_history = get_price_history(redis_conn, start_time, end_time)

# Convert to DataFrame for analysis
df = get_price_dataframe(price_history)

# Calculate moving averages
df['ma_10'] = calculate_moving_average(df, window=10)
df['ma_30'] = calculate_moving_average(df, window=30)

# Calculate volatility
df['volatility'] = df['price'].rolling(window=20).std()

# Detect anomalies
anomalies = detect_price_anomalies(df, threshold=2.0)
```

These analytics help identify trends, potential trading opportunities, and market stability measures.

### Real-time Alerting

The system includes a sophisticated price alerting mechanism:

```python
# Create alert system
alert_system = BitcoinPriceAlertSystem(redis_conn)

# Add threshold alerts
current_price = get_current_bitcoin_price(redis_conn)
upper_threshold = current_price * 1.005  # 0.5% increase
lower_threshold = current_price * 0.995  # 0.5% decrease
alert_system.add_threshold_alert(upper_threshold, is_upper=True)
alert_system.add_threshold_alert(lower_threshold, is_upper=False)

# Add percent change alert
alert_system.add_percent_change_alert(0.2, period_minutes=2)  # 0.2% change within 2 minutes

# Start monitoring
alert_system.start_monitoring()
```

The alert system uses Redis Pub/Sub to monitor price updates in real-time, triggering notifications when specified conditions are met.

## Demonstration

The project includes several demonstrations showcasing its capabilities.

### Data Collection

The data collection process automatically pulls Bitcoin price information from CoinGecko and stores it in Redis:

```python
# Fetch the current Bitcoin price
current_data = fetch_bitcoin_price()
print(f"Current Bitcoin price: ${current_data['usd']:,.2f}")

# Store in Redis
store_bitcoin_price(redis_conn, current_data)

# Fetch historical data
historical_data = fetch_bitcoin_historical(days=7)

# Process and store historical data
count = process_historical_data(historical_data)
print(f"Stored {count} historical data points in Redis")
```

This data becomes the foundation for all subsequent analytics.

### Analytics Dashboard

The system generates visualizations to provide insights into Bitcoin price movements:

```python
# Create figure and axes
fig, ax = plt.subplots(figsize=(12, 6))

# Plot price data
ax.plot(df.index, df['price'], label='Price', color='blue', alpha=0.7)

# Plot moving averages
ax.plot(df.index, df['ma_10'], label='10-point MA', color='red')
ax.plot(df.index, df['ma_30'], label='30-point MA', color='green')

# Plot volatility
ax2 = ax.twinx()
ax2.plot(df.index, df['volatility'], label='Volatility', color='purple', alpha=0.5)

# Plot anomalies
anomaly_points = df[anomalies]
ax.scatter(anomaly_points.index, anomaly_points['price'], 
           color='red', marker='o', s=50, label='Anomalies')

# Set labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Price (USD)')
ax.set_title('Bitcoin Price Analysis')
```

These visualizations help identify trends, support and resistance levels, and potential trading signals.

### Alert Monitoring

The alert system demonstrates real-time monitoring capabilities:

```python
# Show alert settings
print(f"Alert Thresholds:")
print(f"- Upper threshold: ${upper_threshold:,.2f}")
print(f"- Lower threshold: ${lower_threshold:,.2f}")
print(f"- Percent change: 0.2% within 2 minutes")

# Run price simulation to demonstrate alerts
print(f"\nRunning price simulation for {duration} seconds...")
print("This will simulate price fluctuations to demonstrate the alert system")

# After simulation, show triggered alerts
for alert in alerts:
    if alert['triggered']:
        print(f"Alert triggered: {alert['message']}")
```

This demonstration shows how the system can be used for real-time trading signals or risk management.

## Conclusions

The Redis-based Bitcoin price analytics system demonstrates several key advantages:

1. **Performance**: Redis's in-memory data structures provide extremely fast read/write operations, essential for real-time financial analytics.

2. **Flexibility**: The system can be easily extended with additional data sources, analytics, or visualization components.

3. **Scalability**: The architecture supports scaling from a single user to many concurrent users through Redis's pub/sub capabilities.

4. **Persistence**: Despite being an in-memory database, Redis's persistence options ensure data durability.

5. **Real-time capabilities**: The combination of fast data access and publish/subscribe messaging creates a truly real-time system.

