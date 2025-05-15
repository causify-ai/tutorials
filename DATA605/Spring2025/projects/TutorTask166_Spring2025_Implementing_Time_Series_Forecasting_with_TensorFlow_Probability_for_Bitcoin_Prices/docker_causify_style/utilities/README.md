# Bitcoin Forecasting Utilities

This directory contains common utility functions used throughout the Bitcoin Forecasting application to ensure consistent handling of data and formats across different components.

## Utility Modules

### `data_utils.py`

Utilities for data handling and type conversions:

- `safe_round()`: Safely rounds values regardless of their type (scalar, array, etc.)
- `ensure_tz_aware()`: Ensures datetime objects are timezone-aware by adding UTC timezone
- `normalize_timestamps()`: Normalizes timestamps in a DataFrame for consistent handling
- `compare_timestamps()`: Safely compares two timestamps regardless of their timezone awareness
- `filter_by_timestamp()`: Filters DataFrame by timestamp, handling timezone differences safely
- `format_price()`: Formats a price value for display, handling various input types

### `model_utils.py`

Utilities for model operations:

- `extract_scalar_from_prediction()`: Extracts a scalar value from a model prediction
- `validate_confidence_interval()`: Validates confidence intervals for correctness
- `safe_model_prediction()`: Safely calls model prediction methods with error handling
- `calculate_error_metrics()`: Calculates standard error metrics between actual and predicted values

### `initialize_environment.py`

Environment initialization utilities:

- `check_package()`: Checks if a Python package is installed
- `install_package()`: Installs a package using pip
- `initialize_environment()`: Sets up the environment by checking and installing required dependencies

### `timestamp_format.py`

Timestamp formatting utilities:

- `parse_timestamp()`: Parses timestamps from various formats
- `to_iso8601()`: Converts timestamps to ISO8601 format
- `format_timestamp()`: Formats timestamps consistently

### `unified_config.py`

Configuration utilities:

- `get_service_config()`: Gets configuration for a specific service

## Usage

Import these utilities in your application code:

```python
# Import data handling utilities
from utilities.data_utils import safe_round, format_price, filter_by_timestamp

# Import model utilities
from utilities.model_utils import safe_model_prediction, calculate_error_metrics

# Use the utilities in your code
price = safe_round(model_prediction, 2)
formatted_price = format_price(price)
```

## Benefits

Using these common utilities ensures:

1. **Consistency**: Same handling of data types across the application
2. **Robustness**: Better error handling for edge cases
3. **Maintainability**: Centralized implementation of common functionality
4. **Type Safety**: Proper handling of numpy arrays, timestamps, and other special types 