import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def fetch_bitcoin_data(days=365):
    """Fetch Bitcoin historical price data from CoinGecko API"""
    print("Fetching Bitcoin price data...")

    # CoinGecko API endpoint for Bitcoin market data
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"

    # Parameters for the API request
    params = {
        'vs_currency': 'usd',  # Price in USD
        'days': days,          # Historical data for specified days
        'interval': 'daily'    # Daily data
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract price data from the response
        prices = data.get('prices', [])

        if not prices:
            print("No price data found in the response.")
            return None

        # Create a DataFrame from the price data
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])

        # Convert timestamp (milliseconds) to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Drop the original timestamp column and set date as index
        df = df.drop('timestamp', axis=1)
        df = df.set_index('date')

        print(f"Successfully fetched {len(df)} days of Bitcoin price data.")
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CoinGecko API: {e}")
        return None

def preprocess_data(df):
    """Preprocess the Bitcoin price data for time series analysis"""
    print("Preprocessing data...")

    if df is None or df.empty:
        print("No data to preprocess.")
        return None, None, None, None, None

    # Create features from the time series data
    df['price_previous_day'] = df['price'].shift(1)
    df['price_2days_ago'] = df['price'].shift(2)
    df['price_3days_ago'] = df['price'].shift(3)

    # Add rolling averages as features
    df['rolling_mean_3d'] = df['price'].rolling(window=3).mean()
    df['rolling_mean_7d'] = df['price'].rolling(window=7).mean()

    # Add day of week as a feature (0 = Monday, 6 = Sunday)
    df['day_of_week'] = df.index.dayofweek

    # Drop rows with NaN values (first few rows due to shifting)
    df = df.dropna()

    # Prepare features (X) and target variable (y)
    X = df[['price_previous_day', 'price_2days_ago', 'price_3days_ago',
            'rolling_mean_3d', 'rolling_mean_7d', 'day_of_week']]
    y = df['price']

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, shuffle=False
    )

    return X_train, X_test, y_train, y_test, scaler

def train_model(X_train, y_train):
    """Train a linear regression model"""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate the model and return metrics"""
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    return {
        'predictions': predictions,
        'mse': mse,
        'r2_score': r2
    }

def plot_predictions(y_test, predictions):
    """Plot actual vs predicted prices"""
    plt.figure(figsize=(12, 6))
    plt.plot(y_test.index, y_test.values, label='Actual Prices', color='blue')
    plt.plot(y_test.index, predictions, label='Predicted Prices', color='red', linestyle='--')
    plt.title('Bitcoin Price Prediction: Actual vs. Predicted')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()