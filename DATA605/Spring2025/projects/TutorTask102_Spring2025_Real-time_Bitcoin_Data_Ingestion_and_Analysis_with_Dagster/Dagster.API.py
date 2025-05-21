#!/usr/bin/env python
# coding: utf-8

# # Dagster Bitcoin API
# 
# This notebook demonstrates how to interact with the CoinGecko API using Dagster. It provides practical examples of retrieving cryptocurrency data, calculating financial metrics, and detecting anomalies for enhanced crypto analysis.
# 
# ## Notebook Objectives
# It focuses on showcasing the utility functions used to:
# - Fetch Bitcoin prices from the CoinGecko API
# - Transform the data into a structured format
# - Persist the data to disk
# 
# # References
# 
# - CoinGecko API Docs: https://www.coingecko.com/en/api
# - Dagster Documentation: https://docs.dagster.io
# - Getting started with Dagster: https://docs.dagster.io/getting-started
# 
# # Citations
# CoinGecko. (2024). CoinGecko API v3. Retrieved from https://www.coingecko.com/en/api/documentation

# ## Setup and Imports
# 
# This section sets up the notebook environment and imports core utility functions needed for interacting with the CoinGecko API via Dagster.

# In[9]:


from Dagster_utils import (
    fetch_bitcoin_price,
    process_price_data,
    get_historical_bitcoin_data,
    calculate_moving_average,
    detect_trend,
    detect_anomalies_zscore,
    plot_price_with_moving_average
)


# ## Fetch Current Price

# In[10]:


# Fetch current price from CoinGecko API
live_price = fetch_bitcoin_price()
print("Live Price Data:", live_price)


# ## Format Price into DataFrame

# In[11]:


# Convert price dict into DataFrame
df_price = process_price_data(live_price)
df_price


# ##  Fetch Historical Data

# In[12]:


# Get last 30 days of historical BTC prices
df_hist = get_historical_bitcoin_data(days=30)
df_hist.head()


# ## Test Moving Average

# In[13]:


# Compute 5-day moving average on historical data
df_ma = calculate_moving_average(df_hist, window_days=5)
df_ma.head()


# ## Trends and Anomoli Detection

# In[16]:


# Analyze basic trend using linear regression slope
trend_result = detect_trend(df_ma)
print("Trend:", trend_result)

# Identify outliers in price movement
df_anom = detect_anomalies_zscore(df_ma)
df_anom[df_anom["anomaly"] == True].head()


# ## Visualizations

# In[17]:


# Visualize price + moving average line
plot_price_with_moving_average(df_anom)


# In[ ]:




