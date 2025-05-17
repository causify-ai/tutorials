# Bitcoin Price Forecasting System

An advanced real-time Bitcoin price forecasting system leveraging TensorFlow Probability for time series modeling with uncertainty quantification. The system provides accurate price predictions with confidence intervals and comprehensive performance metrics.

## System Architecture

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

This project implements a microservices-based architecture with the following components:

1. **Data Collector**: Fetches real-time Bitcoin price data from Coinbase via WebSocket API
2. **Bitcoin Forecast App**: Processes data and generates predictions using TensorFlow Probability
3. **Dashboard**: Real-time visualization of prices, predictions, and performance metrics
   - **Streamlit Dashboard**: Interactive data visualization with automatic updates
   - **Web App Dashboard**: Modern web interface with real-time updates
4. **Kafka**: Message broker for communication between services
5. **ZooKeeper**: Coordination service for Kafka

## Key Features

### Advanced Time Series Modeling
- Structural time series models with trend, seasonal, and autoregressive components
- Day-of-week seasonality effects
- Local linear trend with flexible priors
- AR(5) for better short-term dynamics
- SemiLocalLinearTrend for cryptocurrency volatility
- Choice between Variational Inference (fast) and MCMC (more accurate)
- Multi-start optimization to avoid local minima

### Enhanced Data Preprocessing
- Multiple outlier detection methods (Modified Z-Score, IQR, Percentage change)
- Missing value handling with exponential weighted imputation
- Cryptocurrency-specific technical indicators
- Robust scaling using median/IQR
- Automatic data validation

### Robust Prediction Framework
- 99% confidence intervals for uncertainty quantification
- Fallback prediction mechanisms using ensemble methods
- Adaptive learning rates based on volatility
- Sanity checks to prevent extreme predictions
- Gradient clipping for optimization stability

### Comprehensive Evaluation
- Mean Absolute Error (MAE) tracking
- Root Mean Squared Error (RMSE) calculation
- Percentage error analysis
- Error distribution visualization
- Anomaly detection for suspicious predictions

### User-Friendly Dashboard
- Real-time price and prediction charts
- Confidence interval visualization
- Error tracking and metrics
- Error distribution analysis
- Cold start handling for improved UX
- 30-minute time window for all charts
- Consistent update frequency (1 second)

## Data Flow Sequence

1. Bitcoin price data is fetched from CoinGecko and published to Kafka
2. The forecasting service consumes the data and loads recent historical context
3. The model is updated with new data and makes a prediction for the next time point
4. The prediction, with confidence intervals, is stored in the predictions file
5. Performance metrics are calculated and stored in the metrics file
6. The dashboard applications read the updated files and refresh the visualization
7. The cycle repeats at the next data ingestion point

## Model Architecture

The Bitcoin forecasting model uses a structural time series approach based on TensorFlow Probability:

1. **Local Linear Trend**: Models the underlying trend in Bitcoin prices
2. **Seasonal Component**: Captures regular cyclical patterns in Bitcoin trading
3. **Autoregressive Component**: Models short-term dependencies where current prices depend on recent past prices

### Inference Techniques

The model uses two primary Bayesian inference techniques:

1. **Variational Inference (VI)**: Fast approximation of the posterior distribution
2. **Markov Chain Monte Carlo (MCMC)**: More accurate uncertainty estimates when needed

## Performance Metrics

The system tracks several performance metrics:

### Mean Absolute Error (MAE)

The Mean Absolute Error between true target values (y) and predictions (ŷ) is defined as:
```
MAE = (1/N) * Σ|y_i - ŷ_i|
```

MAE fluctuations in the visualization are expected due to:
- Point-wise MAE representation (individual prediction errors)
- Bitcoin's inherent price volatility
- Real-time updates capturing many small price movements
- Model adaptation periods when market conditions change

Other metrics include:
- **Root Mean Square Error (RMSE)**: Gives higher weight to larger errors
- **Percentage Error**: Relative error as a percentage of actual price
- **Standard Deviation**: Represents confidence in predictions
- **Z-score**: Identifies anomalous predictions

## Components in Detail

### Data Collector

The data collector connects to Coinbase WebSocket API to fetch real-time Bitcoin price data:

- Aggregates tick data into 1-second OHLCV bars
- Validates and cleans incoming data
- Detects and filters outliers
- Saves data to CSV for persistence
- Publishes data to Kafka for real-time processing
- Provides periodic statistics reporting

### Bitcoin Forecast App

The forecast application processes incoming data and generates predictions:

- Uses TensorFlow Probability for Bayesian time series modeling
- Implements both primary and fallback prediction mechanisms
- Tracks prediction errors for model evaluation
- Updates model continuously as new data arrives
- Handles outliers and anomalous inputs

### Dashboard

Two dashboard implementations are available:

#### Streamlit Dashboard
- Real-time price chart with 30-minute window
- Prediction visualization with confidence intervals
- Error metrics tracking and visualization
- Error distribution analysis
- System status monitoring
- Auto-refreshes every 1 second

#### Web App Dashboard
- Modern UI with responsive design
- Real-time data updates (1 second refresh)
- Interactive charts with Plotly
- Comprehensive metrics display
- Consistent visual styling with the Streamlit dashboard

### Utilities

Common utility functions ensure consistent data handling across all components:

- **Data Utils**: Safe data handling, rounding, filtering
- **Timestamp Format**: Consistent ISO8601 timestamp handling
- **Model Utils**: Safe model prediction, error metrics calculation
- **Price Format**: Consistent price formatting
- **Unified Config**: Centralized configuration management

## Model Configuration

The model can be configured through the `config.yaml` file, which includes settings for:

```yaml
model:
  instant:
    learning_rate: 0.01     # Learning rate for model training
    vi_steps: 100           # Number of variational inference steps
    num_samples: 50         # Number of samples for forecasting
    use_mcmc: false         # Use MCMC for more accurate but slower inference
    mcmc_steps: 1000        # Number of MCMC steps
    mcmc_burnin: 300        # Number of burn-in steps for MCMC
    use_day_of_week: true   # Add day-of-week seasonal component
    use_technical_indicators: true  # Use technical indicators
    short_ma_window: 5      # Short moving average window
    long_ma_window: 20      # Long moving average window
    volatility_window: 10   # Window for volatility calculation
```

## Usage

### Starting the System

1. Start the system using Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. Access the dashboards:
   - Streamlit Dashboard: http://localhost:8501
   - Web App Dashboard: http://localhost:5000

3. Monitor real-time predictions and performance metrics

### Restarting with Optimized Settings

To restart the system with optimized settings:

```bash
./restart_optimized.sh
```

This script:
- Stops existing containers
- Cleans up Docker resources
- Backs up and resets prediction data
- Trims raw data for better performance
- Rebuilds containers with optimized settings

## Recent Improvements

### Universal Data Handling Utilities
- Centralized utility functions for consistent data operations
- Safe rounding, price formatting, timestamp normalization
- Consistent timezone handling in DataFrames

### Model Operation Utilities
- Safe model prediction with comprehensive error handling
- Consistent extraction of scalar values from predictions
- Validation of confidence intervals
- Standardized error metric calculations

### Improved Error Handling
- Comprehensive try/except blocks with detailed error logging
- Fallback mechanisms for model prediction failures
- Graceful handling of type errors and timestamp comparison issues

### Dashboard Enhancements
- Consistent update frequency (1 second) between dashboards
- Improved visualization of MAE and error metrics
- Consistent color schemes across implementations
- Better error rating system for high-value assets like Bitcoin

## Development

### Directory Structure

```
docker_causify_style/
├── bitcoin_forecast_app/      # Prediction service
│   ├── models/                # TensorFlow Probability model
│   ├── mains/                 # Application entry points
│   └── utilities/             # App-specific utilities
├── dashboard/                 # Streamlit visualization interface
├── web_app/                   # Web application
│   ├── backend/               # API backend
│   └── frontend/              # Web frontend
├── data_collector/            # Real-time data collection service 
├── configs/                   # Configuration files
│   └── config.yaml            # Main configuration file
├── utilities/                 # Shared utility functions
│   ├── timestamp_format.py    # Timestamp handling utilities
│   ├── price_format.py        # Price formatting utilities
│   ├── data_utils.py          # Data handling utilities
│   ├── model_utils.py         # Model operation utilities
│   └── unified_config.py      # Configuration parser
├── docker-compose.yml         # Docker services configuration
└── restart_optimized.sh       # System restart script
```

### Configuration

The system uses a unified configuration approach:

1. Edit `configs/config.yaml` to change settings
2. Restart services with `docker-compose restart <service-name>`

## Timestamp Format

All timestamps in the system use the ISO8601 format with 'T' separator:

```
YYYY-MM-DDThh:mm:ss+00:00
```

The system ensures consistent timestamp handling across all components through the utilities/timestamp_format.py module.

## Troubleshooting

### Dashboard Shows No Data

If the dashboard shows no data:

1. Check if data collector is running: `docker-compose logs data-collector`
2. Verify data files exist: `ls -l data/raw/instant_data.csv`
3. Restart the dashboard: `docker-compose restart dashboard`

### High Prediction Errors

If you notice unusually high prediction errors:

1. Check if there are outliers in the raw data
2. Restart the system with clean data: `./restart_optimized.sh`
3. Monitor the metrics after restarting

### Timestamp Mismatch Between Actual and Predicted Data

If actual and predicted data have different timestamps:

1. Restart the bitcoin forecast app: `docker-compose restart bitcoin-forecast-app`
2. Check logs for timestamp parsing errors: `docker-compose logs bitcoin-forecast-app`
3. Run the timestamp fix script: `./scripts/fix_timestamps.sh`

## Docker Commands Reference

### Service Management

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d <service-name>

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart <service-name>

# View logs
docker-compose logs -f
docker-compose logs -f <service-name>
```

### Rebuilding Services

```bash
# Rebuild and restart all services
docker-compose down
docker-compose up -d --build

# Rebuild specific service
docker-compose build <service-name>
docker-compose up -d <service-name>

# Clean build (no cache)
docker-compose build --no-cache
docker-compose up -d
```

### System Maintenance

```bash
# View container status
docker-compose ps

# Clean up unused Docker resources
docker system prune -f
```
