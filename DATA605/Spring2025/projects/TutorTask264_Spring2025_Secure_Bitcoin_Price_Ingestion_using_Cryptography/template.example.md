# Secure Bitcoin Price Ingestion and Analysis System

## Table of Contents

- [Project Overview](#project-overview)
  * [Objectives](#objectives)
  * [Key Features](#key-features)
- [System Architecture](#system-architecture)
  * [Components](#components)
  * [Data Flow](#data-flow)
  * [Security Implementation](#security-implementation)
- [Implementation Details](#implementation-details)
  * [Data Collection](#data-collection)
  * [Security Layer](#security-layer)
  * [Analysis Features](#analysis-features)
  * [Visualization Dashboard](#visualization-dashboard)
- [Example Usage and Results](#example-usage-and-results)
  * [Setup and Configuration](#setup-and-configuration)
  * [Data Processing Pipeline](#data-processing-pipeline)
  * [Analysis Outputs](#analysis-outputs)
- [Technical Specifications](#technical-specifications)

## Project Overview

### Objectives

This project implements a secure and comprehensive Bitcoin price analysis system that combines real-time data ingestion, cryptographic protection, and advanced time series analysis. The system is designed to provide financial analysts and researchers with secure access to Bitcoin price data while ensuring data integrity and confidentiality.

### Key Features

- Real-time Bitcoin price data ingestion from CoinGecko API
- Military-grade encryption using AES-CBC
- Secure key derivation with PBKDF2
- Digital signatures for data integrity
- Interactive Streamlit dashboard
- Advanced time series analysis and forecasting
- Anomaly detection and technical indicators

## System Architecture

### Components

1. **Data Collection Layer**
   - CoinGecko API integration
   - Real-time price fetching
   - Historical data aggregation
   - Data validation and preprocessing

2. **Security Layer**
   - AES-CBC encryption/decryption
   - PBKDF2 key derivation
   - Digital signatures
   - Secure data storage

3. **Analysis Layer**
   - Time series processing
   - Technical indicators
   - Statistical analysis
   - Forecasting models

4. **Visualization Layer**
   - Interactive Streamlit dashboard
   - Real-time updates
   - Dynamic charts and graphs
   - Data export capabilities

### Data Flow

1. Real-time price data ingestion from CoinGecko
2. Data encryption and signature generation
3. Secure storage in JSONL format
4. Authorized decryption for analysis
5. Processing and visualization
6. Interactive user interface presentation

### Security Implementation

```python
# Key security components
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

# Constants
SALT = b"some_salt_for_key_derivation"
ITERATIONS = 100_000
BLOCK_SIZE = AES.block_size

# Key derivation
key = derive_key("secure_password")

# Data encryption
encrypted_data = encrypt_data(price_data, key)

# Digital signature
signature = hash_data(price_data)
```

## Implementation Details

### Data Collection

The system fetches both real-time and historical Bitcoin price data:

```python
# Real-time price fetching
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    response = requests.get(url, params={
        "ids": "bitcoin",
        "vs_currencies": "usd"
    })
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "price_usd": response.json()["bitcoin"]["usd"]
    }

# Historical data collection
def fetch_hourly_data(days=15):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    response = requests.get(url, params=params)
    return process_historical_data(response.json())
```

### Analysis Features

1. **Technical Indicators**
```python
# Moving averages
df['SMA_6'] = df['price_usd'].rolling(window=6).mean()
df['EMA_6'] = df['price_usd'].ewm(span=6).mean()

# Bollinger Bands
df['rolling_mean'] = df['price_usd'].rolling(window=24).mean()
df['rolling_std'] = df['price_usd'].rolling(window=24).std()
df['bb_upper'] = df['rolling_mean'] + 2 * df['rolling_std']
df['bb_lower'] = df['rolling_mean'] - 2 * df['rolling_std']

# MACD
ema_short = df['price_usd'].ewm(span=12).mean()
ema_long = df['price_usd'].ewm(span=26).mean()
df['macd'] = ema_short - ema_long
df['macd_signal'] = df['macd'].ewm(span=9).mean()
```

2. **Time Series Analysis**
```python
# Seasonal decomposition
result = seasonal_decompose(df['price_usd'], 
                          model='additive', 
                          period=24)

# Autocorrelation analysis
plot_acf(df['price_usd'], lags=50)

# Holt-Winters forecasting
model = ExponentialSmoothing(df['price_usd'],
                            trend='add',
                            seasonal='add',
                            seasonal_periods=24)
forecast = model.fit().forecast(24)
```

### Visualization Dashboard

The Streamlit dashboard provides interactive visualizations:

1. **Real-Time Monitoring**
```python
st.subheader("⏱️ Real-Time BTC Price")
if st.button("📥 Fetch Price"):
    price = fetch_bitcoin_price()
    st.success(f"${price['price_usd']:,.2f}")
```

2. **Price Trends**
```python
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(df.index, df['price_usd'], marker='o', markersize=2)
ax.set_title("Bitcoin Price History")
st.pyplot(fig)
```

3. **Technical Analysis**
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['price_usd'],
                        mode='lines', name='Price'))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA_6'],
                        mode='lines', name='SMA'))
st.plotly_chart(fig)
```

4. **Forecasting View**
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['price_usd'],
                        name='Actual'))
fig.add_trace(go.Scatter(x=forecast.index, y=forecast,
                        name='Forecast'))
st.plotly_chart(fig)
```

## Example Usage and Results

### Setup and Configuration

1. Install required packages:
```bash
pip install pycryptodome requests pandas streamlit plotly statsmodels
```

2. Initialize the system:
```python
from SecureBitcoin_utils import *
import streamlit as st

# Configure encryption
key = derive_key("your_secure_password")

# Load data
df = load_historical_data()
```

### Analysis Outputs

The system provides various analytical insights:

1. **Price Statistics**
   - Current price and 24h change
   - Moving averages and trends
   - Volatility metrics

2. **Technical Analysis**
   - Support and resistance levels
   - Trend indicators
   - Momentum oscillators

3. **Forecasting Results**
   - 24-hour price predictions
   - Confidence intervals
   - Seasonal patterns

4. **Security Metrics**
   - Encryption status
   - Data integrity checks
   - Access logs

## Technical Specifications

- **Programming Language**: Python 3.8+
- **Key Libraries**:
  * pycryptodome (encryption)
  * streamlit (visualization)
  * pandas (data processing)
  * statsmodels (analysis)
  * plotly (interactive charts)
- **Data Source**: CoinGecko API
- **Update Frequency**: Real-time + 15-day historical
- **Security Protocol**: AES-CBC with PBKDF2
- **Storage Format**: Encrypted JSONL

The system successfully demonstrates the integration of secure data handling with advanced analytical capabilities. The Streamlit interface provides an intuitive way to interact with encrypted data while maintaining robust security protocols. Through this implementation, we achieve a perfect balance of security, functionality, and analytical capability in Bitcoin price data management.