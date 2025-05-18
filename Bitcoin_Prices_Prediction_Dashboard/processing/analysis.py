import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

def decompose_price(df):
    if len(df) < 24:
        raise ValueError("Data must have at least 24 records for seasonal decomposition.")
    return seasonal_decompose(df['price'], model='additive', period=24)

def compute_moving_avg(df, window=12):
    if 'price' not in df.columns:
        raise ValueError("Missing 'price' column in DataFrame.")
    df['MA'] = df['price'].rolling(window=window, min_periods=1).mean()
    return df

def detect_anomalies(df, std_dev_thresh=2):
    if 'price' not in df.columns:
        raise ValueError("Missing 'price' column in DataFrame.")
    mean = df['price'].mean()
    std = df['price'].std()
    df['zscore'] = (df['price'] - mean) / std
    df['anomaly'] = df['zscore'].abs() > std_dev_thresh
    return df

def add_technical_indicators(df):
    if 'price' not in df.columns:
        raise ValueError("Missing 'price' column in DataFrame.")

    df = df.copy()

    # Simple Moving Averages
    df['MA_7'] = df['price'].rolling(window=7, min_periods=1).mean()
    df['MA_30'] = df['price'].rolling(window=30, min_periods=1).mean()

    # Exponential Moving Averages
    df['EMA_12'] = df['price'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['price'].ewm(span=26, adjust=False).mean()

    # MACD and Signal Line
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Absolute Price Change
    df['Price_Change'] = df['price'].diff().fillna(0)

    # Volatility: Rolling Standard Deviation of Price
    df['Volatility'] = df['price'].rolling(window=10, min_periods=1).std()

    # Returns: Percentage change
    df['Returns'] = df['price'].pct_change().fillna(0) * 100

    # Cumulative Returns: Simulates compounding
    df['Cumulative_Return'] = (1 + df['Returns'] / 100).cumprod()

    return df
