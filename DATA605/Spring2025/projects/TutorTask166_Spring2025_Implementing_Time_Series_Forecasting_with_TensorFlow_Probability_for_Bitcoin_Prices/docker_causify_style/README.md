# Bitcoin Price Forecasting System

An advanced real-time Bitcoin price forecasting system leveraging TensorFlow Probability for time series modeling with uncertainty quantification.

## System Architecture

This project implements a microservices-based Bitcoin price forecasting system with the following components:

1. **Data Collector**: Fetches real-time Bitcoin price data from exchanges
2. **Bitcoin Forecast App**: Processes data and generates predictions using TensorFlow Probability
3. **Dashboard**: Real-time visualization of prices, predictions, and performance metrics

## Key Features

### Advanced Time Series Modeling
- Structural time series models with trend, seasonal, and autoregressive components
- Day-of-week seasonality effects
- Choice between Variational Inference (fast) and MCMC (more accurate)

### Enhanced Data Preprocessing
- Outlier detection and replacement
- Missing value handling
- Technical indicators (moving averages, MACD, RSI, momentum)
- Feature normalization and scaling

### Robust Prediction Framework
- Confidence intervals for uncertainty quantification
- Fallback prediction mechanisms for system resilience
- Adaptive learning rates for better convergence
- Multiple window size forecasting

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

## Model Configuration

The model can be configured through the `unified_config.yaml` file, which includes settings for:

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
```

## System Improvements

The system has been enhanced with several optimizations:

1. **Duplicate Prediction Prevention**: The system now tracks the last processed second to avoid duplicates.

2. **Improved Error Calculation**: MAE calculations have been corrected to properly measure the difference between predicted and actual values.

3. **Enhanced Dashboard**: The dashboard now displays actual error at each timestamp with a zero-line baseline for perfect predictions.

4. **Advanced Model Components**: The prediction model now includes autoregressive components and day-of-week effects.

5. **Cold Start Handling**: The dashboard dynamically adjusts its time range when limited data is available during startup.

6. **Price Value Rounding**: All price-related values are consistently rounded to 2 decimal places.

7. **Error Distribution Analysis**: Statistical analysis of prediction errors with distribution visualization.

8. **Anomaly Detection**: Z-score based anomaly detection for suspicious predictions.

## Usage

1. Start the system using Docker Compose:
   ```
   docker-compose up
   ```

2. Access the dashboard at http://localhost:8501

3. Monitor real-time predictions and performance metrics

## Development

The codebase is organized as follows:

- `bitcoin_forecast_app/`: The main prediction service
  - `models/`: TensorFlow Probability model implementation
  - `mains/`: Application entry points
- `dashboard/`: Streamlit-based visualization interface
- `configs/`: Configuration files
- `utilities/`: Shared utility functions

## Refactoring Overview

This project has been refactored to improve code organization, reduce redundancy, and ensure consistency across services. The key improvements include:

1. **Unified Configuration**: All configuration settings are now in a single `unified_config.yaml` file
2. **Centralized Utilities**: Common functions are now in a shared `utilities` directory
3. **Clear Service Boundaries**: Each service has a well-defined responsibility
4. **Consistent Timestamp Handling**: Standardized ISO8601 format with 'T' separator

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository
2. Run `docker-compose build` to build the services
3. Run `docker-compose up -d` to start the system

### Configuration

The system uses a unified configuration approach:

1. Edit `configs/unified_config.yaml` to change settings
2. Run `scripts/update_config.sh` to apply changes
3. Restart services with `docker-compose up -d`

## Timestamp Format

All timestamps in the system use the ISO8601 format with 'T' separator:

```
YYYY-MM-DDThh:mm:ss
```

If you encounter timestamp format issues, use the `scripts/fix_timestamps.sh` script to standardize them.

## Documentation

- `docs/CODE_STRUCTURE.md`: Detailed explanation of the code structure
- `docs/TIMESTAMP_FORMAT.md`: Information about timestamp handling

## Troubleshooting

### Dashboard Error: 'str' object has no attribute 'date'

This error occurs when timestamps are not properly parsed as datetime objects. To fix it:

1. Run `scripts/fix_timestamps.sh` to standardize timestamp formats
2. Restart the dashboard service: `docker-compose restart dashboard`

### Timestamp Mismatch Between Actual and Predicted Data

If you notice that actual and predicted data have different timestamps:

1. Run `scripts/fix_timestamps.sh` to update all timestamps to the current date
2. Restart the services: `docker-compose restart bitcoin-forecast-app dashboard`

## Common Docker Commands

### Restart Services with Updated Code
```bash
docker-compose restart bitcoin-forecast-app dashboard
docker-compose logs -f
```

### Rebuild and Restart All Services
```bash
docker-compose down
docker-compose up -d --build
docker-compose logs -f
```

### Clean Build (No Cache)
```bash
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f
```
