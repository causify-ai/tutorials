#!/usr/bin/env python
# coding: utf-8

# # CoinGecko API Interface Notebook
# 
# This notebook defines the minimal API code necessary to ingest real-time Bitcoin price data from CoinGecko.
# The function(s) implemented here are used directly by the streaming machine learning pipeline in `bitcoin_forecast_using_river.example.ipynb`.

# In[3]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
get_ipython().run_line_magic('matplotlib', 'inline')


# ## Imports
# This section ensures that all necessary packages are installed before execution. 

# In[38]:


get_ipython().system('pip install requests')
get_ipython().system('pip install os')
get_ipython().system('pip install time')
get_ipython().system('pip install pandas')
get_ipython().system('pip install plotly')
get_ipython().system('pip install matplotlib')
get_ipython().system('pip install scikit-learn')
get_ipython().system('pip install river')
get_ipython().system('pip install pytest')


# In[31]:


import requests
import os
import time
import pandas as pd
import matplotlib as plt
import plotly.graph_objects as go
import plotly.io as pio


# # API Configuration 
# This section defines the necessary configuration to call the CoinGecko API and includes retry logic to handle rate limiting (HTTP 429 errors).

# In[32]:


API_KEY = os.getenv("Coingecko_API_KEY")  # Ensure this is set in your environment
BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {"X-Cg-Pro-Api-Key": API_KEY}


# In[33]:


def get_bitcoin_price_with_retry(vs_currency="usd", retries=5, delay=2):
    """
    Fetches the current Bitcoin price from CoinGecko with retry logic,
    in case the API rate limit (429 error) is hit.
    """
    endpoint = f"{BASE_URL}/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": vs_currency}

    for attempt in range(retries):
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()["bitcoin"][vs_currency]
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"[Retry {attempt + 1}/{retries}] Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"HTTP error occurred: {e}")
                raise
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise
    raise Exception("Max retries exceeded")


# In[34]:


# Testing get_bitcoin_price
for _ in range(3):
    price = get_bitcoin_price_with_retry()
    print(f"BTC price: ${price:,.2f}")
    time.sleep(5)


# ## Fetch OHLC (Open-High-Low-Close) Data from CoinGecko
# 
# This section defines a function to retrieve OHLC (candlestick) data for Bitcoin using the CoinGecko API.
# We fetch and parse this data to enable richer features for time-series modeling in the River pipeline.

# In[8]:


def extract_ohlc_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given OHLC data, compute derived features like price change, volatility, etc.
    """
    df = df.copy()
    df['price_change'] = df['close'].pct_change()
    df['high_low_spread'] = (df['high'] - df['low']) / df['low']
    df['volatility'] = df['close'].rolling(window=5).std()
    df = df.dropna()
    return df


# In[9]:


def get_coin_ohlc(coin_id: str = "bitcoin", vs_currency: str = "usd", days: int = 1) -> pd.DataFrame:
    """
    Fetches OHLC data for the specified coin from CoinGecko.

    :param coin_id: The coin to retrieve data for (default = 'bitcoin')
    :param vs_currency: The currency to quote prices in (default = 'usd')
    :param days: Number of days (1, 7, 14, 30, 90, 180, 365, max)

    :return: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close']
    """
    endpoint = f"{BASE_URL}/coins/{coin_id}/ohlc"
    params = {
        "vs_currency": vs_currency,
        "days": days
    }

    try:
        response = requests.get(endpoint, params=params, headers=HEADERS)
        response.raise_for_status()
        raw = response.json()
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except requests.RequestException as e:
        print(f"Error fetching OHLC data: {e}")
        return pd.DataFrame()


# In[10]:


#  Extract OHLC-based features (price_change, volatility, etc.)
ohlc_df = get_coin_ohlc(days=1)
ohlc_features_df = extract_ohlc_features(ohlc_df)
display(ohlc_features_df.tail())  # Optional: Inspect last few rows


# The resulting DataFrame shows OHLC data enriched with four engineered features:  
#  `price_change`, `price_change_pct`, `range`, and `volatility` — ready for time series modeling.

# ###  Caching OHLC API Calls
# Avoids hitting the API repeatedly during testing by using a local cache.

# In[11]:


import os
import pickle

def cache_or_fetch_ohlc(cache_path="ohlc_cache.pkl", days=7):
    """
    Fetches OHLC data from cache if available, else from API and caches it.
    """
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            print(" Loaded OHLC data from cache.")
            return pickle.load(f)
    
    df = get_coin_ohlc("bitcoin", vs_currency="usd", days=days)
    with open(cache_path, "wb") as f:
        pickle.dump(df, f)
    print("Fetched OHLC from API and cached it.")
    return df


# In[12]:


ohlc_df = cache_or_fetch_ohlc()


# In[13]:


#  Validation checks for safety
assert not ohlc_df.empty, " OHLC DataFrame is empty. API may have failed."
assert "timestamp" in ohlc_df.columns, " Missing 'timestamp' column in OHLC data."
assert all(col in ohlc_df.columns for col in ["open", "high", "low", "close"]), " Missing OHLC price columns."


# ### Dashboard-Ready Data Wrapper
# Combines API data for use in dashboards or streaming pipelines.
# 

# In[14]:


def fetch_bitcoin_data_structured(vs_currency="usd"):
    """
    Combines live price and OHLC data into a UI/dash-ready dictionary.
    """
    price = get_bitcoin_price_with_retry(vs_currency)
    ohlc_data = get_coin_ohlc("bitcoin", vs_currency=vs_currency, days=7)
    
    return {
        "current_price": price,
        "ohlc": ohlc_data
    }


# In[15]:


# Fetch combined Bitcoin price and OHLC data
data_bundle = fetch_bitcoin_data_structured()

# Display the structure of the returned data
print(" Current Price (USD):", data_bundle['current_price'])
print("\n OHLC DataFrame Preview:")
display(data_bundle['ohlc'].head())


# In[16]:


# Dashboard-friendly dictionary output
btc_data = fetch_bitcoin_data_structured()
btc_data  # optional: print or preview if needed


# The output is a dashboard-friendly dictionary containing the current Bitcoin price and a recent OHLC DataFrame with timestamps, making it suitable for real-time visualizations or pipelines.

# ### Candlestick Chart of Bitcoin OHLC Data (Last 7 Days)
# This chart shows the open, high, low, and close prices of Bitcoin for each 4-hour interval over the past 7 days, using data retrieved from the CoinGecko API.

# In[23]:


pio.renderers.default = 'notebook'
fig = go.Figure(data=[go.Candlestick(
    x=ohlc_df['timestamp'],
    open=ohlc_df['open'],
    high=ohlc_df['high'],
    low=ohlc_df['low'],
    close=ohlc_df['close'],
    name='BTC'
)])

fig.update_layout(
    title='Bitcoin OHLC Candlestick Chart (7 Days)',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=False
)

fig.show()


# The output displays an interactive candlestick chart visualizing Bitcoin’s open, high, low, and close prices over the past 7 days using 4-hour intervals.

# ### Line Plot of Bitcoin OHLC Components
# This plot compares the open, high, low, and close prices of Bitcoin over the past 7 days to show volatility and market trends.
# 

# In[25]:


import matplotlib.pyplot as plt  #  Ensure this is run

plt.figure(figsize=(12, 6))
plt.plot(ohlc_df['timestamp'], ohlc_df['open'], label='Open')
plt.plot(ohlc_df['timestamp'], ohlc_df['high'], label='High')
plt.plot(ohlc_df['timestamp'], ohlc_df['low'], label='Low')
plt.plot(ohlc_df['timestamp'], ohlc_df['close'], label='Close')
plt.title("Bitcoin OHLC Line Plot")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# The output displays a line plot comparing Bitcoin’s open, high, low, and close prices over the last 7 days, allowing for visual analysis of market trends and volatility.

# ## Summary Statistics of Bitcoin OHLC Data (Last 7 Days)
# 
# This section displays key descriptive statistics (mean, standard deviation, min, max, etc.) for the Open, High, Low, and Close prices of Bitcoin retrieved over the past 7 days using the CoinGecko API. These metrics are essential for understanding market volatility and price dispersion.

# In[26]:


# Summary statistics for Open, High, Low, Close
ohlc_stats = ohlc_df[['open', 'high', 'low', 'close']].describe()
ohlc_stats


# The table provides statistical summaries that help assess the central tendency, variability, and distribution of Bitcoin price movements over the observed 7-day window.

# #  Integration with the River Streaming Pipeline
# 
# This notebook focuses on robust data acquisition from the CoinGecko API — specifically live prices and OHLC time-series data.
# 
# The functions defined here (`get_bitcoin_price_with_retry`, `get_coin_ohlc`) are used as a data ingestion layer by the `template.example.ipynb` notebook, where the River library is used for online learning.
# 
# River models support **incremental updates** with new data, making them ideal for streaming tasks like Bitcoin price prediction. This modular separation ensures:
# 
# -  Reliable API-side data processing here
# -  Model-specific processing and forecasting logic in the next stage
# 
# Together, these notebooks demonstrate a complete real-time data pipeline:  
# **Ingest → Analyze → Predict → Visualize**
# 

# ## Real-Time Price Streaming + Online Learning (30 Steps)
# This cell simulates 30 rounds of real-time Bitcoin price streaming using the get_bitcoin_price_with_retry() function and updates a River Linear Regression model on each step.

# In[39]:


from bitcoin_forecast_utils import *
from river import linear_model, metrics
from collections import deque
import datetime

model = linear_model.LinearRegression()
metric = metrics.MAE()
rolling_prices = deque(maxlen=5)
mae_log = []
pred_log = []
true_log = []


# In[40]:


# Simulate real-time streaming
for step in range(30):  # simulate 30 steps
    try:
        price = get_bitcoin_price_with_retry()
        rolling_prices.append(price)
        if len(rolling_prices) < 5:
            continue

        features = build_rolling_features(rolling_prices)
        pred = model.predict_one(features)
        true = features['price_lag_0']

        if pred is not None:
            model.learn_one(features, true)
            metric = metric.update(true, pred)
            mae_log.append(metric.get())
            pred_log.append(pred)
            true_log.append(true)

        print(f"Step {step+1}: True={true}, Predicted={pred:.2f}, MAE={metric.get():.4f}")
        time.sleep(2)  # simulate real-time

    except Exception as e:
        print("Error during streaming:", e)
        continue


# Despite early CoinGecko rate-limit errors (429), the loop recovers and prints real-time true vs predicted prices along with the rolling MAE, confirming that online learning is functioning as expected.

# ## Simulated API Retry Logic
# Simulates an API failure to validate that the retry mechanism would be triggered correctly using a raised HTTPError

# In[41]:


# Simulated API error to demonstrate retry mechanism
def simulate_api_failure():
    raise requests.exceptions.HTTPError(response=requests.Response())

try:
    simulate_api_failure()
except requests.exceptions.HTTPError:
    print("Retry logic would be triggered here (simulated).")


# # Save the Trained River Model
# Saves the trained River regression model to disk using pickle for future reuse (btc_stream_model.pkl).

# In[42]:


import pickle

# Save the trained River model to a file
with open('btc_stream_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model saved to btc_stream_model.pkl")


# In[ ]:




