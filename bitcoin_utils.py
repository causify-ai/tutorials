import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import s3fs
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from scipy.stats import zscore


def fetch_bitcoin_data(api_key: str = "YOUR_API_KEY", days: int = 365, interval: str = 'daily') -> pd.DataFrame:
    """
    Fetches historical Bitcoin price data from the CoinGecko API.
    """
    headers = {'x-cg-demo-api-key': api_key}
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': str(days),
        'interval': interval
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")


def save_to_local(df: pd.DataFrame, filename: str):
    """
    Saves a DataFrame to a local CSV file.
    """
    df.to_csv(filename, index=False)
    print(f"✅ Data saved locally as {filename}")


def upload_to_s3(local_path: str, s3_path: str):
    """
    Uploads a local CSV file to an S3 bucket using s3fs.
    """
    try:
        fs = s3fs.S3FileSystem(anon=False)
        with fs.open(s3_path, 'w') as f:
            pd.read_csv(local_path).to_csv(f, index=False)
        print(f"✅ {local_path} uploaded to S3 at {s3_path}")
    except Exception as e:
        print(f"⚠️ Failed to upload to S3: {e}")


def load_from_s3(s3_path: str) -> pd.DataFrame:
    """
    Loads a CSV file from S3 into a DataFrame.
    """
    fs = s3fs.S3FileSystem(anon=False)
    with fs.open(s3_path, 'rb') as f:
        df = pd.read_csv(f)
    print("✅ Successfully loaded data from S3")
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the Timestamp column to datetime and sets it as the DataFrame index.
    """
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    print("✅ Data preprocessed (timestamp set as index)")
    return df


def check_missing(df: pd.DataFrame):
    """
    Prints missing value count for each column.
    """
    print("✅ Missing Values Check:")
    print(df.isnull().sum())


def plot_price(df: pd.DataFrame):
    """
    Plots Bitcoin price over time.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Price'], marker='o', linestyle='-')
    plt.title('Bitcoin Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def decompose_series(df: pd.DataFrame):
    """
    Decomposes the time series into trend, seasonal, and residual components.
    """
    result = seasonal_decompose(df['Price'], model='additive', period=7)
    plt.figure(figsize=(12, 8))
    result.plot()
    plt.suptitle('Bitcoin Price Decomposition (Trend + Seasonality + Residuals)', fontsize=16)
    plt.tight_layout()
    plt.show()


def plot_moving_average(df: pd.DataFrame, window_size: int = 5):
    """
    Plots the moving average along with the original price.
    """
    df = df.copy()
    df['Moving_Avg'] = df['Price'].rolling(window=window_size).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Price'], label='Actual Price', marker='o')
    plt.plot(df.index, df['Moving_Avg'], label=f'{window_size}-Day Moving Average', linestyle='--')
    plt.title(f'Bitcoin Price vs {window_size}-Day Moving Average')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def forecast_arima(df: pd.DataFrame, steps: int = 10):
    """
    Fits an ARIMA model and forecasts future values.
    """
    model = ARIMA(df['Price'], order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    forecast_index = pd.date_range(start=df.index[-1] + timedelta(days=1), periods=steps)

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Price'], label='Historical Price')
    plt.plot(forecast_index, forecast, label='ARIMA Forecast', linestyle='--', marker='x')
    plt.title(f'ARIMA Forecast (Next {steps} Days)')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects anomalies using Z-score and IQR methods.
    """
    df = df.copy()
    df['Z_Score'] = zscore(df['Price'])
    df['Anomaly_Z'] = np.abs(df['Z_Score']) > 3

    rolling_median = df['Price'].rolling(window=7, center=True).median()
    iqr = df['Price'].rolling(window=7, center=True).quantile(0.75) - df['Price'].rolling(window=7, center=True).quantile(0.25)
    lower = rolling_median - 1.5 * iqr
    upper = rolling_median + 1.5 * iqr
    df['Anomaly_IQR'] = (df['Price'] < lower) | (df['Price'] > upper)

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Price'], label='Price')
    plt.scatter(df[df['Anomaly_Z']].index, df[df['Anomaly_Z']]['Price'], color='red', label='Z-Score Anomaly')
    plt.scatter(df[df['Anomaly_IQR']].index, df[df['Anomaly_IQR']]['Price'], color='orange', label='IQR Anomaly', marker='x')
    plt.title('Bitcoin Price Anomalies')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return df
