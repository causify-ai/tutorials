import requests
import pandas as pd
import sqlite3
from datetime import datetime
import time
import numpy as np
from scipy.stats import zscore
from statsmodels.tsa.seasonal import STL

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
CURRENT_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"
DB_FILE = "data/bitcoin_data.db"


def fetch_historical_bitcoin_prices(days=365, interval="daily"):
    """
    Fetches historical Bitcoin prices from CoinGecko for the past 'days'.
    """
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }
    response = requests.get(COINGECKO_URL, params=params)
    response.raise_for_status()
    data = response.json()
    prices = data.get('prices', [])
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def fetch_current_price():
    """
    Fetches the current Bitcoin price.
    """
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }
    response = requests.get(CURRENT_PRICE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    price = data["bitcoin"]["usd"]
    timestamp = pd.Timestamp.utcnow()
    return pd.DataFrame([{"timestamp": timestamp, "price": price}])


def save_to_sqlite(df, db_file=DB_FILE, table_name="bitcoin_prices"):
    """
    Saves a DataFrame to an SQLite table.
    """
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()


def init_db(db_file=DB_FILE, table_name="bitcoin_prices"):
    """
    Initializes the SQLite database if the table doesn't exist.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()


def calculate_moving_average(df, window=7):
    """
    Adds a column with the moving average over the given window.
    """
    df_sorted = df.sort_values("timestamp").copy()
    df_sorted["moving_avg"] = df_sorted["price"].rolling(window=window).mean()
    return df_sorted


def detect_price_spikes(df, threshold=0.05):
    """
    Detects potential price anomalies (spikes or dips) based on relative changes.
    """
    df = df.sort_values("timestamp").copy()
    df["price_change"] = df["price"].pct_change()
    df["anomaly"] = df["price_change"].abs() > threshold
    return df


def run_realtime_ingestion(interval_seconds=3600, iterations=5):
    """
    Periodically fetches current Bitcoin price and stores it into SQLite.
    Useful for simulating a real-time ingestion pipeline.
    """
    init_db()
    for _ in range(iterations):
        df = fetch_current_price()
        save_to_sqlite(df)
        print(f"[{datetime.utcnow()}] Ingested current price: ${df['price'].iloc[0]:,.2f}")
        time.sleep(interval_seconds)



def calculate_moving_averages(df):
    """
    Adds 7-day, 30-day, and 90-day moving averages.
    """
    df = df.copy()
    df = df.sort_values("timestamp")
    df["MA_7"] = df["price"].rolling(window=7).mean()
    df["MA_30"] = df["price"].rolling(window=30).mean()
    df["MA_90"] = df["price"].rolling(window=90).mean()
    return df


def calculate_volatility(df, window=7):
    """
    Adds rolling standard deviation (volatility) of price.
    """
    df = df.copy()
    df = df.sort_values("timestamp")
    df["volatility"] = df["price"].rolling(window=window).std()
    return df


def detect_anomalies_zscore(df, threshold=3):
    """
    Detects anomalies using Z-score.
    """
    df = df.copy()
    df["z_score"] = zscore(df["price"].dropna())
    df["z_score"] = df["z_score"].reindex(df.index)  # Align index
    df["anomaly_z"] = df["z_score"].abs() > threshold
    return df


def generate_trend_indicators(df):
    """
    Adds daily returns and cumulative returns.
    """
    df = df.copy()
    df = df.sort_values("timestamp")
    df["daily_return"] = df["price"].pct_change()
    df["cumulative_return"] = (1 + df["daily_return"]).cumprod()
    return df


def decompose_time_series(df, period=30, model='additive', plot=False):
    """
    Performs STL decomposition on the time series.
    Optional: plots trend, seasonal, and residual components.
    """
    df = df.copy()
    df = df.sort_values("timestamp")
    df.set_index("timestamp", inplace=True)
    series = df["price"].dropna()

    stl = STL(series, period=period, robust=True)
    result = stl.fit()

    decomposition_df = pd.DataFrame({
        "timestamp": series.index,
        "trend": result.trend,
        "seasonal": result.seasonal,
        "residual": result.resid
    }).reset_index(drop=True)

    if plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 8))
        plt.subplot(3, 1, 1)
        plt.plot(series.index, result.trend, label='Trend')
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(series.index, result.seasonal, label='Seasonality')
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(series.index, result.resid, label='Residuals')
        plt.legend()

        plt.tight_layout()
        plt.show()

    return decomposition_df