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

    # Create features using only past data
    df['returns'] = df['price'].pct_change()  # Daily returns
    df['volatility'] = df['returns'].rolling(window=7).std()  # 7-day volatility
    df['price_7d_ago'] = df['price'].shift(7)  # Price 7 days ago
    df['price_14d_ago'] = df['price'].shift(14)  # Price 14 days ago
    df['price_30d_ago'] = df['price'].shift(30)  # Price 30 days ago
    
    # Technical indicators
    df['MA7'] = df['price'].rolling(window=7).mean()
    df['MA30'] = df['price'].rolling(window=30).mean()
    df['RSI'] = calculate_rsi(df['price'], periods=14)
    
    # Market trend features
    df['trend_7d'] = (df['price'] - df['price_7d_ago']) / df['price_7d_ago']
    df['trend_14d'] = (df['price'] - df['price_14d_ago']) / df['price_14d_ago']
    
    # Drop rows with NaN values
    df = df.dropna()

    # Prepare features (X) and target variable (y)
    feature_columns = [
        'returns', 'volatility', 
        'price_7d_ago', 'price_14d_ago', 'price_30d_ago',
        'MA7', 'MA30', 'RSI', 
        'trend_7d', 'trend_14d'
    ]
    
    X = df[feature_columns]
    y = df['price']

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split the data - use earlier data for training, later data for testing
    train_size = int(len(df) * 0.8)
    X_train = X_scaled[:train_size]
    X_test = X_scaled[train_size:]
    y_train = y[:train_size]
    y_test = y[train_size:]

    return X_train, X_test, y_train, y_test, scaler

def calculate_rsi(prices, periods=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def train_model(X_train, y_train):
    """Train a more complex model"""
    from sklearn.ensemble import GradientBoostingRegressor
    
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        random_state=42
    )
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