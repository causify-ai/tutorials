<!-- toc -->

- [Bitcoin Forecast API Example](#bitcoin-forecast-api-example)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
  * [Project Description](#project-description)
  * [Architecture and Data](#architecture-and-data)
  * [API Usage Example](#api-usage-example)
  * [Results and Demonstration](#results-and-demonstration)

<!-- tocstop -->

# Bitcoin Forecast API Example

This document provides a detailed example of using the Bitcoin Forecast API for time series forecasting with TensorFlow Probability.

## Table of Contents

The markdown code can have a TOC. This can be generated automatically with the linter or other tools.

### Hierarchy

Hierarchy of the markdown file should be followed.
```
# Level 1 (Used as title)
## Level 2
### Level 3
```

**Note** Level 1 Heading (Title) should be `Bitcoin Forecast API Example`

## General Guidelines

- Follow the instructions in the project [README](./README.md) for example usage and best practices.
- This example demonstrates how to use the API for forecasting Bitcoin prices with sample data.
- The main reference implementation is in [`tfp.example.ipynb`](./tfp.example.ipynb).
- All code is documented and can be adapted for your own data and use cases.

## Project Description

This example shows how to use the Bitcoin Forecast API to:
- Load and preprocess sample Bitcoin price data
- Fit a probabilistic time series model
- Generate forecasts with confidence intervals
- Evaluate prediction accuracy

## Architecture and Data

- The example uses a small, synthetic dataset representing Bitcoin closing prices over time.
- The architecture follows the core API: data preprocessing, model fitting, forecasting, and evaluation.
- All steps are demonstrated in [`tfp.example.ipynb`](./tfp.example.ipynb).

## API Usage Example

See the notebook [`tfp.example.ipynb`](./tfp.example.ipynb) for a full, runnable example. Below is a summary of the workflow:

```python
import numpy as np
from tfp_API import BitcoinForecastModel

# Sample configuration (minimal)
config = {
    'model': {
        'instant': {
            'lookback': 20,
            'num_seasons': 4,
            'learning_rate': 0.01,
            'vi_steps': 50,
            'num_samples': 10
        }
    }
}

# Generate synthetic Bitcoin price data
np.random.seed(42)
price_series = np.cumsum(np.random.randn(20) * 50 + 10000)

# Initialize and fit the model
model = BitcoinForecastModel(config)
model.fit(price_series)

# Make a forecast
mean, lower, upper = model.forecast(num_steps=1)
print(f"Forecast: ${mean:.2f} [${lower:.2f}, ${upper:.2f}]")

# Evaluate the prediction
actual_price = price_series[-1]  # Use last value as 'actual'
metrics = model.evaluate_prediction(actual_price, mean)
print("Metrics:", metrics)
```

## Results and Demonstration

- The example demonstrates the full workflow: data loading, model fitting, forecasting, and evaluation.
- Results include the predicted price, confidence interval, and error metrics.
- For more details and visualizations, see [`tfp.example.ipynb`](./tfp.example.ipynb). 