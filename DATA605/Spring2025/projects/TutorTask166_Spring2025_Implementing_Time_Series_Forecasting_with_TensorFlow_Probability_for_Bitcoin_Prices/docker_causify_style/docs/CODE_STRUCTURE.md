# Bitcoin Price Forecasting System: Code Structure

## System Overview

The Bitcoin Price Forecasting System is composed of several microservices that work together to collect, process, predict, and visualize Bitcoin price data:

1. **Data Collector**: Collects real-time Bitcoin price data from exchanges
2. **Bitcoin Forecast App**: Processes the data and generates price predictions
3. **Dashboard**: Visualizes the actual and predicted prices
4. **Web App**: Provides a web interface for viewing predictions

## Directory Structure

```
docker_causify_style/
├── configs/                  # Unified configuration files
│   └── unified_config.yaml   # Single configuration source of truth
├── utilities/                # Shared utility functions
│   ├── timestamp_format.py   # Timestamp handling utilities
│   ├── price_format.py       # Price formatting utilities
│   └── unified_config.py     # Configuration parser
├── data/                     # Data storage
│   ├── raw/                  # Raw price data
│   └── predictions/          # Prediction outputs
├── data_collector/           # Data collector service
│   ├── collector.py          # Main data collection script
│   └── scripts/              # Data collector utility scripts
├── bitcoin_forecast_app/     # Bitcoin forecasting service
│   ├── models/               # Forecasting models
│   └── mains/                # Main application scripts
├── dashboard/                # Streamlit dashboard
│   └── app.py                # Dashboard application
├── web_app/                  # Web application
│   ├── backend/              # API backend
│   └── frontend/             # Web frontend
├── scripts/                  # System-wide utility scripts
│   ├── fix_timestamps.py     # Script to fix timestamp formats
│   ├── fix_timestamps.sh     # Shell wrapper for timestamp fixing
│   └── update_config.sh      # Script to update configuration
└── docs/                     # Documentation
    ├── CODE_STRUCTURE.md     # This file
    └── TIMESTAMP_FORMAT.md   # Timestamp format documentation
```

## Component Interactions

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Data Source   │────▶│ Data Collector │────▶│     Kafka      │
└────────────────┘     └────────────────┘     └────────────────┘
                                                      │
                                                      ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   Dashboard    │◀────│   Shared Data  │◀────│Bitcoin Forecast│
└────────────────┘     └────────────────┘     └────────────────┘
       │                                              │
       │                                              │
       ▼                                              ▼
┌────────────────┐                           ┌────────────────┐
│  Web Frontend  │◀─────────────────────────▶│  Web Backend   │
└────────────────┘                           └────────────────┘
```

## Key Components

### 1. Unified Configuration

The system uses a unified configuration approach where all settings are defined in a single `unified_config.yaml` file. This ensures consistency across services and makes system-wide changes easier to implement.

```python
from utilities.unified_config import get_service_config

# Get service name from environment or use default
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'dashboard')

# Load config using unified config parser
config = get_service_config(SERVICE_NAME)
```

### 2. Shared Utilities

Common functionality is centralized in the `utilities/` directory:

- **timestamp_format.py**: Handles consistent timestamp formatting across the system
- **price_format.py**: Provides price formatting functions
- **unified_config.py**: Loads and parses the unified configuration

### 3. Data Flow

1. **Data Collection**: The data collector retrieves Bitcoin prices and publishes them to Kafka
2. **Prediction**: The forecast app consumes the data, makes predictions, and saves them to CSV files
3. **Visualization**: The dashboard reads the CSV files and displays the data in real-time

### 4. Docker Services

Each component runs as a separate Docker service, defined in `docker-compose.yml`:

- **zookeeper**: Manages Kafka cluster
- **kafka**: Message broker for real-time data
- **data-collector**: Collects Bitcoin price data
- **bitcoin-forecast-app**: Generates price predictions
- **dashboard**: Displays visualizations
- **web-backend**: Provides API endpoints
- **web-frontend**: Serves the web interface

## Configuration Structure

The unified configuration is organized into sections:

1. **Global Settings**: App name, version, logging settings
2. **Data Paths**: File locations for raw data and predictions
3. **Data Format**: Column names, data types, timestamp formats
4. **Kafka Settings**: Connection parameters
5. **Service-Specific Settings**: Settings for each microservice

## Timestamp Handling

Timestamps are standardized across the system to use ISO8601 format with 'T' separator:

```
YYYY-MM-DDThh:mm:ss
```

The `utilities/timestamp_format.py` module provides functions to ensure consistent formatting:

```python
from utilities.timestamp_format import format_timestamp

# Format a timestamp with T separator
timestamp_str = format_timestamp(timestamp, use_t_separator=True)
```

## Updating the System

To apply configuration changes:

1. Edit the `configs/unified_config.yaml` file
2. Run the update script: `./scripts/update_config.sh`
3. Restart the services: `docker-compose up -d` 