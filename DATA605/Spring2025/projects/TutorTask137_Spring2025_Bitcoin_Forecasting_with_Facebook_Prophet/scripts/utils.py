#Libraries 

import pandas as pd
import requests
import matplotlib.pyplot as plt
from prophet import Prophet

# Load historical Kaggle data
def load_historical_data(filepath):
    """
    Load and process historical Bitcoin CSV data.
    Converts to daily frequency and formats for Prophet.
    """
    df = pd.read_csv(filepath)
    df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
    df = df[['datetime', 'Close']].dropna()
    df.rename(columns={'datetime': 'ds', 'Close': 'y'}, inplace=True)
    df = df.set_index('ds').resample('D').agg({'y': 'last'}).reset_index()
    return df

# Fetch live price data from CoinGecko
def fetch_live_data(days=365, currency='usd'):
    """
    Fetch real-time Bitcoin price data from CoinGecko API.
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {'vs_currency': currency, 'days': days, 'interval': 'daily'}
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'y'])
    df['ds'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['ds', 'y']]

# Merge historical and live data
def merge_and_clean_data(historical_df, live_df):
    """
    Merge, deduplicate, and resample Bitcoin price data to daily frequency.
    """
    final_df = pd.concat([historical_df, live_df])
    final_df.drop_duplicates(subset='ds', keep='last', inplace=True)
    final_df = final_df.set_index('ds').resample('D').agg({'y': 'last'}).reset_index()
    return final_df

# Create Prophet model
def create_prophet_model():
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    return model

# Train Prophet model
def train_prophet_model(model, data):
    model.fit(data)
    return model

# Make future forecast
def make_forecast(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

# Plot forecast
def plot_forecast(model, forecast):
    fig = model.plot(forecast)
    plt.title("Bitcoin Price Forecast")
    plt.grid(True)
    plt.show()
