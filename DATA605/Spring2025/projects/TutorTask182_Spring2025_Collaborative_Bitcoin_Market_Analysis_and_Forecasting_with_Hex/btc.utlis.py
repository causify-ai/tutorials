

import requests
import pandas as pd
from prophet import Prophet

# --------------------------------------
# API Layer
# --------------------------------------

def get_btc_price():
    """Fetch the current Bitcoin price in USD from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    data = response.json()
    return data['bitcoin']['usd']

def get_btc_history(days=90):
    """Fetch historical Bitcoin prices from CoinGecko (daily for given days)."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "daily"}
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
    
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df[["date", "price"]]

def get_gold_price(api_key=None):
    """Fetch recent daily gold prices from Alpha Vantage."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": "XAUUSD",
        "apikey": api_key or "demo",  # Replace with real key in prod
        "outputsize": "compact"
    }
    response = requests.get(url, params=params)
    data = response.json().get("Time Series (Daily)", {})
    
    df = pd.DataFrame.from_dict(data, orient="index")
    df["gold_price"] = df["4. close"].astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().reset_index().rename(columns={"index": "date"})
    return df[["date", "gold_price"]]

# --------------------------------------
# Analysis Functions
# --------------------------------------

def calculate_volatility(df):
    """Add 30-day rolling average and standard deviation (volatility) to BTC price dataframe."""
    df = df.sort_values("date")
    df["avg_price_30d"] = df["price"].rolling(window=30).mean()
    df["volatility_30d"] = df["price"].rolling(window=30).std()
    return df

def detect_anomalies(df, threshold=-5):
    """Detect days with percent change less than threshold (e.g., -5%)."""
    df = df.copy()
    df["pct_change"] = df["price"].pct_change() * 100
    return df[df["pct_change"] <= threshold]

def calculate_correlation(btc_df, gold_df):
    """Merge BTC and gold prices and calculate rolling 30-day correlation."""
    df = pd.merge(btc_df, gold_df, on="date", how="inner").sort_values("date")
    df["rolling_corr_30d"] = df["price"].rolling(30).corr(df["gold_price"])
    return df

# --------------------------------------
# Forecasting
# --------------------------------------

def forecast_btc_prices(df, periods=30):
    """Use Prophet to forecast future BTC prices."""
    df = df[["date", "price"]].rename(columns={"date": "ds", "price": "y"}).copy()
    
    model = Prophet()
    model.fit(df)
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return forecast, model
