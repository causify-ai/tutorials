#!/usr/bin/env python
# coding: utf-8

# # Bitcoin Forecast API Example
# 
# This notebook demonstrates how to use the Bitcoin Forecast API for time series forecasting with TensorFlow Probability.
# We use synthetic data to show the full workflow: data loading, model fitting, forecasting, and evaluation.
# 

# In[ ]:


import numpy as np
import matplotlib.pyplot as plt
# from tfp_API import BitcoinForecastModel  # Uncomment if using as a package
from tfp_API import BitcoinForecastModel  # Assume the class is available in the environment


# ## Sample Configuration and Data
# 
# We create a minimal configuration and generate synthetic Bitcoin price data for demonstration.
# 

# In[ ]:


# Minimal configuration
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

plt.figure(figsize=(10, 4))
plt.plot(price_series, marker='o', label='Synthetic BTC Price')
plt.title('Synthetic Bitcoin Price Series')
plt.xlabel('Time Index')
plt.ylabel('Price (USD)')
plt.legend()
plt.show()


# ## Model Initialization and Fitting
# 
# We initialize the model and fit it to the synthetic data.
# 

# In[ ]:


model = BitcoinForecastModel(config)
model.fit(price_series)


# ## Forecasting
# 
# We generate a 1-step-ahead forecast with confidence intervals.
# 

# In[ ]:


mean, lower, upper = model.forecast(num_steps=1)
print(f'Forecast: ${mean:.2f} [${lower:.2f}, ${upper:.2f}]')


# ## Evaluation
# 
# We evaluate the forecast using the last value in the synthetic series as the 'actual' price.
# 

# In[ ]:


actual_price = price_series[-1]
metrics = model.evaluate_prediction(actual_price, mean)
print('Metrics:', metrics)


# ## Visualization
# 
# We visualize the synthetic data and the forecast with its confidence interval.
# 

# In[ ]:


plt.figure(figsize=(10, 4))
plt.plot(price_series, marker='o', label='Synthetic BTC Price')
plt.axhline(mean, color='orange', linestyle='--', label='Forecast')
plt.fill_between([len(price_series)-1, len(price_series)], [lower, lower], [upper, upper], color='orange', alpha=0.2, label='Confidence Interval')
plt.title('Forecast and Confidence Interval')
plt.xlabel('Time Index')
plt.ylabel('Price (USD)')
plt.legend()
plt.show()

