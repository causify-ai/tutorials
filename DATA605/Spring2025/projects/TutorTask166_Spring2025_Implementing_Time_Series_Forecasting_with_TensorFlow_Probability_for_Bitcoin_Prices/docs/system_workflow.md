# Bitcoin Forecasting System Workflow

This document outlines the end-to-end workflow of the Bitcoin Price Forecasting system, from data ingestion to visualization.

## System Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CoinGecko  │───▶│    Kafka    │───▶│  Forecasting│───▶│  Dashboard  │
│  API Data   │    │   Broker    │    │    Model    │    │     App     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                          │     ▲
                                          │     │
                                          ▼     │
                                      ┌─────────────┐
                                      │   Storage   │
                                      │  CSV Files  │
                                      └─────────────┘
```

## Component Workflow

### 1. Data Ingestion (CoinGecko API)

1. **Data Source**: Real-time Bitcoin price data is fetched from the CoinGecko API
2. **Frequency**: Data is retrieved at configurable intervals (typically every minute)
3. **Data Format**: JSON data containing timestamp, price, volume, and market data
4. **Data Validation**: Basic validation ensures data contains required fields
5. **Data Publishing**: Valid data is published to a Kafka topic

### 2. Data Stream Processing (Kafka)

1. **Message Broker**: Kafka serves as the central message broker
2. **Topics**: Data is organized into topics (e.g., 'bitcoin-instant-data')
3. **Producers**: Data ingest services publish to appropriate topics
4. **Consumers**: The forecasting model subscribes to these topics
5. **Message Format**: Standardized JSON format with timestamp and price data

### 3. Forecasting Pipeline

The forecasting pipeline consists of several stages:

#### 3.1 Data Loading and Preprocessing

1. **Historical Data Loading**: Loads recent historical data (configurable window)
2. **Data Cleaning**: Handles missing values and outliers
3. **Feature Preparation**: Processes raw data into suitable format for the model
4. **Timestamp Normalization**: Ensures consistent time representation

#### 3.2 Model Building and Training

1. **Model Construction**: Creates a structural time series model with:
   - Local Linear Trend component
   - Seasonal component
   - Autoregressive component
2. **Parameter Inference**: Uses Variational Inference (VI) or MCMC to estimate parameters
3. **Adaptation**: Adjusts learning rates and VI steps based on recent performance
4. **Model Versioning**: Keeps track of model versions for debugging and analysis

#### 3.3 Forecasting Process

1. **Forward Prediction**: Generates next-step predictions with uncertainty estimates
2. **Confidence Intervals**: Calculates prediction intervals from the posterior distribution
3. **Error Handling**: Multiple fallback mechanisms ensure prediction availability
4. **Metrics Calculation**: Computes performance metrics for each prediction

#### 3.4 Continuous Learning

1. **Model Update**: Incorporates new observations as they arrive
2. **Drift Detection**: Identifies changes in price dynamics
3. **Adaptive Methods**: Adjusts model parameters based on recent performance
4. **Model Reinitialization**: Handles TensorFlow variable errors with restart mechanisms

### 4. Storage Layer

1. **Data Storage**: Raw price data saved to CSV files
2. **Prediction Storage**: Predictions and confidence intervals saved to CSV
3. **Metrics Storage**: Performance metrics saved for analysis
4. **File Organization**: Structured directory layout with configurable paths
5. **Persistence**: Ensures data survives container restarts

### 5. Visualization Dashboard

1. **Data Loading**: Reads prediction and metrics files
2. **Interactive Charts**: Displays:
   - Price predictions with confidence intervals
   - Actual vs. predicted prices
   - Error metrics over time
   - Model performance statistics
3. **Real-time Updates**: Dashboard refreshes at configurable intervals
4. **User Interface**: Web-based interface built with Dash/Plotly
5. **Customization**: Configurable time ranges and display options

## Data Flow Sequence

1. Bitcoin price data is fetched from CoinGecko and published to Kafka
2. The forecasting service consumes the data and loads recent historical context
3. The model is updated with new data and makes a prediction for the next time point
4. The prediction, with confidence intervals, is stored in the predictions file
5. Performance metrics are calculated and stored in the metrics file
6. The dashboard application reads the updated files and refreshes the visualization
7. The cycle repeats at the next data ingestion point

## Configuration Management

The system uses a hierarchical configuration system:

1. **Base Configuration**: Default settings in YAML files
2. **Environment Variables**: Override configuration for deployment environments
3. **Service-specific Configuration**: Each component has dedicated configuration sections
4. **Dynamic Configuration**: Some parameters are adjusted at runtime based on performance

## Error Handling and Resilience

The system incorporates multiple layers of error handling:

1. **Data Validation**: Ensures input data meets quality requirements
2. **Exception Handling**: Comprehensive try/except blocks with detailed logging
3. **Fallback Mechanisms**: Alternative prediction methods when primary methods fail
4. **Model Reinitialization**: Automatic recovery from TensorFlow variable errors
5. **Service Monitoring**: Logging of system health and performance metrics

## Deployment Architecture

The application is deployed as a set of Docker containers:

1. **bitcoin-forecast-app**: Core forecasting engine
2. **dashboard**: Visualization frontend
3. **kafka**: Message broker for data streaming
4. **zookeeper**: Manages Kafka configuration

## Performance Considerations

Several optimizations enhance system performance:

1. **Selective Model Updates**: Model is only updated at configurable intervals
2. **Adaptive Computation**: VI steps adjusted based on price volatility
3. **Efficient Data Handling**: Windowing techniques limit data size
4. **Memory Management**: Explicit garbage collection and resource cleanup
5. **Parallel Processing**: Utilizes TensorFlow's parallel computation capabilities 