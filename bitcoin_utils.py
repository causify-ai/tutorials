# bitcoin_utils.py

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from econml.dml import LinearDML
from econml.dr import DRLearner
from pytrends.request import TrendReq
import matplotlib.pyplot as plt

# -----------------------------
# 1. Fetch real-time Bitcoin price (last 90 days)
# -----------------------------
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "90",  # fetch last 90 days
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    prices = data['prices']  # [timestamp, price]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
    df = df.groupby("date").mean().reset_index()
    return df[['date', 'price']]

# -----------------------------
# 2. Fetch Google Trends data for "Bitcoin"
# -----------------------------
def fetch_google_trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    today = datetime.today()
    start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    kw_list = ["Bitcoin"]
    pytrends.build_payload(kw_list, cat=0, timeframe='today 3-m', geo='', gprop='')
    df_trend = pytrends.interest_over_time().reset_index()
    df_trend['date'] = df_trend['date'].dt.date
    return df_trend[['date', 'Bitcoin']]

# -----------------------------
# 3. Merge Bitcoin price and Google Trends
# -----------------------------
def prepare_dataset():
    df_price = fetch_bitcoin_price()
    df_trend = fetch_google_trends()
    
    df = pd.merge(df_price, df_trend, on='date')
    df.rename(columns={'Bitcoin': 'trend'}, inplace=True)
    df.dropna(inplace=True)
    df['price_change'] = df['price'].pct_change().fillna(0)
    
    # Scale features
    scaler = StandardScaler()
    df[['trend_scaled']] = scaler.fit_transform(df[['trend']])
    
    return df

# -----------------------------
# 4. Train DoubleML model
# -----------------------------
def train_dml_model(df):
    X = df[['trend_scaled']]
    T = df['trend_scaled']
    Y = df['price_change']

    model_y = RandomForestRegressor(n_estimators=100, random_state=0)
    model_t = LassoCV(cv=5)

    dml = LinearDML(model_y=model_y, model_t=model_t, random_state=0)
    dml.fit(Y, T, X=X)
    treatment_effect = dml.effect(X)
    
    return treatment_effect, dml

from econml.dml import CausalForestDML

def train_cf_model(df):
    X = df[['trend_scaled']]
    T = df['trend_scaled']
    Y = df['price_change']

    model_y = RandomForestRegressor(n_estimators=100, random_state=0)
    model_t = LassoCV(cv=5)

    cf = CausalForestDML(model_y=model_y, model_t=model_t, random_state=0)
    cf.fit(Y, T, X=X)
    treatment_effect = cf.effect(X)

    return treatment_effect, cf


# -----------------------------
# 5. Train Doubly Robust model
# -----------------------------
def train_dr_model(df):
    X = df[['trend_scaled']]
    T = df['trend_scaled']
    Y = df['price_change']

    model_y = RandomForestRegressor(n_estimators=100, random_state=0)
    model_t = LassoCV(cv=5)

    dr = DRLearner(model_regression=model_y, model_propensity=model_t)
    dr.fit(Y, T, X=X)
    treatment_effect = dr.effect(X)

    return treatment_effect, dr

# -----------------------------
# 6. Plot treatment effect
# -----------------------------
def plot_effects(df, effect, title="Estimated Causal Effect"):
    plt.figure(figsize=(10, 4))
    plt.plot(df['date'], effect, label='Estimated Effect')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Causal Effect on Return")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
