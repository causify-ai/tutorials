

<!-- toc -->

- [Bitcoin RDS API](#bitcoin-rds-api)
     - [Introduction](#introduction)
     - [System Architecture](#system-architecture)
     - [Core API Components](#core-api-components)
          - [Database Connection](#database-connection)
          - [Data Retrieval](#data-retrieval)
          - [Data Storage](#data-storage)
          - [Time Series Analysis](#time-series-analysis)
     - [CoinGecko API Integration](#coingecko-api-integration)
     - [Error Handling](#error-handling)
     - [Best Practices](#best-practices)

<!-- tocstop -->

# Bitcoin RDS API

This documentation covers the Bitcoin RDS API, a system for storing, retrieving, and analyzing Bitcoin price data using Amazon RDS PostgreSQL database and the CoinGecko cryptocurrency API.

## Introduction

The Bitcoin RDS API provides a wrapper around Amazon RDS PostgreSQL services and CoinGecko's cryptocurrency API to enable real-time Bitcoin data processing. The API facilitates:

- Database connection and table management in Amazon RDS
- Real-time Bitcoin price data retrieval from CoinGecko
- Data storage and aggregation in PostgreSQL
- Time series analysis and visualization of Bitcoin market data

## System Architecture

The system consists of three main components:

1. **Amazon RDS PostgreSQL Database**: Serves as the persistent data store for Bitcoin price information
2. **CoinGecko API Connection**: Provides real-time and historical Bitcoin market data
3. **Python Wrapper Layer**: Connects these services through utility functions that:
      - Manage database connections and schema
      - Fetch data from CoinGecko
      - Process and store data in RDS
      - Provide analysis functions for the stored data

## Core API Components

The Bitcoin RDS API consists of four core functional components that work together to provide complete data management capabilities: Databsae Conenection, Data Retrieval, Data Storage, and Time series analysis. These components handle different aspects of the data lifecycle from connection and retrieval to storage and analysis, creating a unified interface for Bitcoin price data operations.

### Database Connection

The API provides a simple interface for connecting to an Amazon RDS PostgreSQL instance:

```python
def get_db_connection():
    """Connect to the Amazon RDS PostgreSQL database."""
    try:
        logging.info("Connecting to RDS database")
        conn = psycopg2.connect(
            host=RDS_CONFIG['host'],
            port=RDS_CONFIG['port'],
            database=RDS_CONFIG['database'],
            user=RDS_CONFIG['user'],
            password=RDS_CONFIG['password']
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise
```

Database schema creation is handled through dedicated functions:

```python
def create_tables_if_not_exist():
    """Create necessary tables if they don't already exist."""
    logging.info("Creating tables if they don't exist")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create raw_bitcoin_prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_bitcoin_prices (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                price_usd NUMERIC NOT NULL,
                volume_usd NUMERIC NOT NULL,
                market_cap_usd NUMERIC NOT NULL
            )
        ''')

        # Create hourly_bitcoin_prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hourly_bitcoin_prices (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                open_price_usd NUMERIC NOT NULL,
                high_price_usd NUMERIC NOT NULL,
                low_price_usd NUMERIC NOT NULL,
                close_price_usd NUMERIC NOT NULL,
                volume_usd NUMERIC NOT NULL
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Tables created successfully")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        raise
```

### Data Retrieval

Functions for retrieving Bitcoin price data from both CoinGecko and the RDS database:

```python
def fetch_bitcoin_data_from_coingecko():
    """Fetch current Bitcoin data from CoinGecko API."""
    logging.info("Fetching Bitcoin data from CoinGecko")
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/bitcoin',
            params={
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false'
            },
            headers=API_CONFIG['headers']
        )

        response.raise_for_status()
        data = response.json()

        return {
            'timestamp': datetime.now(),
            'price_usd': data['market_data']['current_price']['usd'],
            'volume_usd': data['market_data']['total_volume']['usd'],
            'market_cap_usd': data['market_data']['market_cap']['usd']
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from CoinGecko: {e}")
        raise
```

Retrieving historical data from the database:

```python
def get_bitcoin_price_history(days=30):
    """Retrieve Bitcoin price history from the database."""
    logging.info(f"Retrieving {days} days of Bitcoin price history")
    try:
        conn = get_db_connection()

        query = '''
            SELECT timestamp, price_usd, volume_usd, market_cap_usd
            FROM raw_bitcoin_prices
            WHERE timestamp >= NOW() - INTERVAL %s DAY
            ORDER BY timestamp DESC
        '''

        df = pd.read_sql_query(query, conn, params=(days,))
        conn.close()

        logging.info(f"Retrieved {len(df)} records of Bitcoin price history")
        return df
    except Exception as e:
        logging.error(f"Error retrieving price history: {e}")
        raise
```

### Data Storage

API methods for storing Bitcoin data in the RDS database:

```python
def insert_raw_bitcoin_data(data):
    """Insert raw Bitcoin price data into the database."""
    logging.info("Inserting raw Bitcoin data into database")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            INSERT INTO raw_bitcoin_prices (timestamp, price_usd, volume_usd, market_cap_usd)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        '''

        cursor.execute(query, (
            data['timestamp'],
            data['price_usd'],
            data['volume_usd'],
            data['market_cap_usd']
        ))

        record_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        logging.info(f"Data inserted successfully with ID: {record_id}")
        return record_id
    except Exception as e:
        logging.error(f"Error inserting data: {e}")
        raise
```

Aggregating data into hourly records:

```python
def aggregate_hourly_data():
    """Aggregate raw price data into hourly OHLC format."""
    logging.info("Aggregating hourly Bitcoin data")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Find the latest hour in the hourly table
        cursor.execute("SELECT MAX(timestamp) FROM hourly_bitcoin_prices")
        latest_hour = cursor.fetchone()[0]

        if latest_hour is None:
            # If no data exists, start from the earliest data point
            cursor.execute("SELECT MIN(timestamp) FROM raw_bitcoin_prices")
            start_time = cursor.fetchone()[0]
            if start_time is None:
                logging.info("No data to aggregate")
                cursor.close()
                conn.close()
                return
        else:
            # Start from the next hour after the latest in the hourly table
            start_time = latest_hour + timedelta(hours=1)

        # Find the most recent full hour (truncate to hour)
        end_time = datetime.now().replace(minute=0, second=0, microsecond=0)

        if start_time >= end_time:
            logging.info("No new data to aggregate")
            cursor.close()
            conn.close()
            return

        # Calculate number of hours to aggregate
        hours_to_aggregate = int((end_time - start_time).total_seconds() / 3600)
        logging.info(f"Aggregating {hours_to_aggregate} hours of data")

        current_hour = start_time
        for _ in range(hours_to_aggregate):
            next_hour = current_hour + timedelta(hours=1)

            # Get OHLC data for the current hour
            cursor.execute('''
                SELECT
                    MIN(timestamp) as open_time,
                    FIRST_VALUE(price_usd) OVER (ORDER BY timestamp) as open_price,
                    MAX(price_usd) as high_price,
                    MIN(price_usd) as low_price,
                    LAST_VALUE(price_usd) OVER (ORDER BY timestamp RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as close_price,
                    SUM(volume_usd) as volume
                FROM raw_bitcoin_prices
                WHERE timestamp >= %s AND timestamp < %s
            ''', (current_hour, next_hour))

            result = cursor.fetchone()

            if result[0] is not None:  # If there's data for this hour
                cursor.execute('''
                    INSERT INTO hourly_bitcoin_prices
                    (timestamp, open_price_usd, high_price_usd, low_price_usd, close_price_usd, volume_usd)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    current_hour,
                    result[1],  # open
                    result[2],  # high
                    result[3],  # low
                    result[4],  # close
                    result[5] if result[5] is not None else 0  # volume
                ))

            current_hour = next_hour

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Hourly data aggregated successfully")
    except Exception as e:
        logging.error(f"Error aggregating hourly data: {e}")
        raise
```

### Time Series Analysis

The API provides basic time series analysis functions:

```python
def calculate_moving_average(df, window=24):
    """Calculate moving average of Bitcoin price."""
    logging.info(f"Calculating {window}-hour moving average")
    try:
        # Ensure data is sorted by timestamp
        df = df.sort_values('timestamp')

        # Calculate moving average
        df['MA'] = df['price_usd'].rolling(window=window).mean()

        return df
    except Exception as e:
        logging.error(f"Error calculating moving average: {e}")
        raise
```

## CoinGecko API Integration

The Bitcoin RDS API integrates with CoinGecko's cryptocurrency API for real-time and historical Bitcoin data. The integration uses standard HTTP requests and handles rate limiting appropriately:

```python
API_CONFIG = {
    'base_url': 'https://api.coingecko.com/api/v3',
    'headers': {
        'Accept': 'application/json',
        'User-Agent': 'Bitcoin RDS Integration'
    },
    'api_key': None  # Optional API key for higher rate limits
}

def fetch_historical_bitcoin_data(days=30):
    """Fetch historical Bitcoin data from CoinGecko."""
    logging.info(f"Fetching historical Bitcoin data for the past {days} days")
    try:
        # Fetch daily price data
        endpoint = f"{API_CONFIG['base_url']}/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }

        if API_CONFIG['api_key']:
            params['x_cg_pro_api_key'] = API_CONFIG['api_key']

        response = requests.get(
            endpoint,
            params=params,
            headers=API_CONFIG['headers']
        )

        response.raise_for_status()
        data = response.json()

        # Format data
        prices = data['prices']
        volumes = data['total_volumes']
        market_caps = data['market_caps']

        formatted_data = []

        for i in range(len(prices)):
            timestamp = datetime.fromtimestamp(prices[i][0] / 1000)  # Convert milliseconds to seconds
            price = prices[i][1]
            volume = volumes[i][1]
            market_cap = market_caps[i][1]

            formatted_data.append({
                'timestamp': timestamp,
                'price_usd': price,
                'volume_usd': volume,
                'market_cap_usd': market_cap
            })

        return formatted_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching historical data from CoinGecko: {e}")
        raise
```

## Error Handling

The API implements robust error handling with detailed logging:

```python
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def fetch_and_store_historical_bitcoin_data(days=30):
    """Fetch and store historical Bitcoin price data."""
    try:
        historical_data = fetch_historical_bitcoin_data(days)
        records_inserted = 0

        for data_point in historical_data:
            insert_raw_bitcoin_data(data_point)
            records_inserted += 1

        logging.info(f"Successfully inserted {records_inserted} historical records")
        return records_inserted
    except Exception as e:
        logging.error(f"Error in fetch_and_store_historical_bitcoin_data: {e}")
        raise
```
