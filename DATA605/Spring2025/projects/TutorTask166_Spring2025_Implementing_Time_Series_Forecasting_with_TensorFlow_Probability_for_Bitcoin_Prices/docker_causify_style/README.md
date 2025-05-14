# Bitcoin Price Forecasting System

## Refactoring Overview

This project has been refactored to improve code organization, reduce redundancy, and ensure consistency across services. The key improvements include:

1. **Unified Configuration**: All configuration settings are now in a single `unified_config.yaml` file
2. **Centralized Utilities**: Common functions are now in a shared `utilities` directory
3. **Clear Service Boundaries**: Each service has a well-defined responsibility
4. **Consistent Timestamp Handling**: Standardized ISO8601 format with 'T' separator

## System Components

- **Data Collector**: Collects real-time Bitcoin price data
- **Bitcoin Forecast App**: Generates price predictions using TensorFlow Probability
- **Dashboard**: Visualizes actual and predicted prices using Streamlit
- **Web App**: Provides a web interface for viewing predictions

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
