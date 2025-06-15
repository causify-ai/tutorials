import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

def load_bitcoin_data(file_path):
    """
    Load Bitcoin price data from CSV in Prophet-ready format (ds, y).
    """
    df = pd.read_csv(file_path)
    df['ds'] = pd.to_datetime(df['ds'])
    return df

def train_prophet_model(df):
    """
    Train a Prophet model on the given dataframe.
    """
    model = Prophet()
    model.fit(df)
    return model

def make_forecast(model, periods=30):
    """
    Use the trained Prophet model to make a future forecast.
    """
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

def plot_forecast(model, forecast):
    """
    Plot the forecast using Prophet’s built-in plot function.
    """
    fig1 = model.plot(forecast)
    plt.title("Bitcoin Price Forecast")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.show()
    return fig1

def plot_forecast_components(model, forecast):
    """
    Plot forecast trend, weekly and yearly seasonality.
    """
    fig2 = model.plot_components(forecast)
    plt.show()
    return fig2
