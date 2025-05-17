<!-- toc -->

- [Bitcoin Forecast API Tutorial](#bitcoin-forecast-api-tutorial)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
  * [API Overview](#api-overview)
    + [Main Classes and Functions](#main-classes-and-functions)
    + [Example Usage](#example-usage)

<!-- tocstop -->

# Bitcoin Forecast API Tutorial

This document provides an overview and usage guide for the core API of the Bitcoin price forecasting system, implemented with TensorFlow Probability.

## Table of Contents

The markdown code can have a TOC. This can be generated automatically with the linter or other tools.

### Hierarchy

Hierarchy of the markdown file should be followed.
```
# Level 1 (Used as title)
## Level 2
### Level 3
```

Level 1 Headings indicate the title as `# <tool> Tutorial` (e.g., `Bitcoin Forecast API Tutorial`).

## General Guidelines

- Follow the instructions in the project [README](./README.md) for API usage and best practices.
- This API is designed for time series forecasting of Bitcoin prices, with uncertainty quantification and robust evaluation.
- The main reference implementation is in [`tfp.API.ipynb`](./tfp.API.ipynb).
- All code is documented with clear docstrings and type annotations.

## API Overview

The API provides a unified interface for:
- Data preprocessing and outlier handling
- Model building and fitting (using TensorFlow Probability structural time series)
- Forecasting with confidence intervals
- Evaluation of prediction accuracy

### Main Classes and Functions

- **BitcoinForecastModel**: Core class for model definition, fitting, forecasting, and evaluation.
- **BitcoinForecastApp**: Orchestrator for data loading, model lifecycle, and prediction output (see notebook for details).

### Example Usage

```python
from tfp_API import BitcoinForecastModel
# Load your configuration dictionary
config = {...}
# Initialize the model
model = BitcoinForecastModel(config)
# Load your price series as a numpy array
price_series = ...
# Fit the model
model.fit(price_series)
# Make a forecast
mean, lower, upper = model.forecast(num_steps=1)
# Evaluate the prediction
metrics = model.evaluate_prediction(actual_price, mean)
print("Forecast:", mean, "[", lower, ",", upper, "]")
print("Metrics:", metrics)
```

For more details and advanced usage, see [`tfp.API.ipynb`](./tfp.API.ipynb). 