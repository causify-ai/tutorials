"""
bitcoin_utils.py

Utility functions for handling Bitcoin historical price data.

This file contains helper functions to:
- Load and clean CSV datasets.
- Update dataset with latest data from CoinGecko.
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import MinMaxScaler
import logging


# --------------------------------------------------------------------
# Logging Setup
# --------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# Data Loading & Cleaning
# --------------------------------------------------------------------

def load_and_clean_csv(file_path: str):
    """
    Load and clean the historical Bitcoin dataset from CSV.

    :param file_path: Path to the CSV file (e.g., 'data/btc-usd-max.csv')
    :return: Cleaned DataFrame with datetime index and numeric columns
    """
    logger.info(f"Loading dataset from {file_path}")

    # Load CSV into DataFrame
    df = pd.read_csv(file_path)

    # Convert 'snapped_at' column to datetime
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], utc=True)

    # Sort by timestamp to ensure chronological order
    df = df.sort_values('snapped_at')

    # Set datetime as index (good practice for time series)
    df.set_index('snapped_at', inplace=True)

    # Ensure columns are numeric
    for col in ['price', 'market_cap', 'total_volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where price is missing (critical target)
    df = df.dropna(subset=['price'])

    # Fill missing market_cap and total_volume if needed
    df['market_cap'] = df['market_cap'].fillna(method='ffill')
    df['total_volume'] = df['total_volume'].fillna(method='ffill')

    # Drop duplicate timestamps (if any)
    df = df[~df.index.duplicated(keep='last')]

    # Log shape and column names
    logger.info(f"Dataset loaded: {df.shape[0]} rows; columns: {list(df.columns)}")

    return df

# --------------------------------------------------------------------
# Update Dataset with Latest Data
# --------------------------------------------------------------------

def update_dataset_with_latest(csv_path: str):
    """
    Fetch the latest Bitcoin data point from CoinGecko and append it
    to the existing dataset if it's a new timestamp.

    :param csv_path: Path to the existing CSV file (e.g., 'data/btc-usd-max.csv')
    """
    logger.info(f"Loading existing dataset from {csv_path}")
    df = pd.read_csv(csv_path)
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], utc=True)

    logger.info("Fetching latest data point from CoinGecko")
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": 1}
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the latest data point
    latest_price = data['prices'][-1]
    latest_cap = data['market_caps'][-1]
    latest_volume = data['total_volumes'][-1]

    # Build a single-row DataFrame
    latest_data = pd.DataFrame({
        'snapped_at': [pd.to_datetime(latest_price[0], unit='ms', utc=True)],
        'price': [latest_price[1]],
        'market_cap': [latest_cap[1]],
        'total_volume': [latest_volume[1]]
    })

    logger.info(f"Latest data point: {latest_data.iloc[0].to_dict()}")

    # Check if this timestamp already exists
    if latest_data['snapped_at'].iloc[0] in df['snapped_at'].values:
        logger.info("Latest data point is already in the dataset. No update needed.")
    else:
        logger.info("Appending new data point to the dataset.")
        df = pd.concat([df, latest_data], ignore_index=True)
        df = df.sort_values('snapped_at')
        df.to_csv(csv_path, index=False)
        logger.info(f"Dataset updated and saved to {csv_path}")


# --------------------------------------------------------------------
# Feature Engineering
# --------------------------------------------------------------------
def technical_features(df: pd.DataFrame):
    """
    Adds feature-engineered columns to the DataFrame:
    - Daily returns
    - Rolling means
    - Rolling volatility

    :param df: Cleaned DataFrame
    :return: DataFrame with new feature columns
    """
    logger.info("Adding technical feature columns")

    # Daily returns
    df['returns'] = df['price'].pct_change()

    # Rolling means
    df['SMA_7'] = df['price'].rolling(window=7).mean()
    df['SMA_30'] = df['price'].rolling(window=30).mean()

    # Rolling volatility (std dev)
    df['volatility_7'] = df['price'].rolling(window=7).std()
    df['volatility_30'] = df['price'].rolling(window=30).std()

    # Lag features (previous day's price)
    df['lag_1day'] = df['price'].shift(1)

    logger.info("Feature engineering complete")
    return df


# --------------------------------------------------------------------
# Sequence Generator for LSTM
# --------------------------------------------------------------------

def generate_sequences(df: pd.DataFrame, features: list, target: str = 'price', window_size: int = 60):
    """
    Generate multivariate sequences and targets for LSTM from a cleaned DataFrame.

    :param df: Cleaned DataFrame with engineered features
    :param features: List of column names to use as input features
    :param target: Column name to predict (usually 'price')
    :param window_size: Number of timesteps per input sequence
    :return: X (sequences), y (targets), scaler object
    """
    logger.info(f"Generating sequences using features {features} and target '{target}'")

    # Select feature matrix and target vector
    X_data = df[features].values
    y_data = df[target].values.reshape(-1, 1)

    # Scale both X and y
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    X_scaled = scaler_X.fit_transform(X_data)
    y_scaled = scaler_y.fit_transform(y_data)

    X, y = [], []
    for i in range(window_size, len(df)):
        X.append(X_scaled[i - window_size:i])
        y.append(y_scaled[i])

    X = np.array(X)
    y = np.array(y)

    logger.info(f"Generated {X.shape[0]} sequences with shape {X.shape[1:]}")

    return X, y, scaler_X, scaler_y

# --------------------------------------------------------------------
# LSTM Model Tuning with KerasTuner
# --------------------------------------------------------------------
import keras_tuner as kt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense

def tune_lstm_model(X_train, y_train, X_val, y_val, max_trials=5, epochs=10):
    """
    Use KerasTuner to find the best LSTM architecture.

    :param X_train: Training features
    :param y_train: Training targets
    :param X_val: Validation features
    :param y_val: Validation targets
    :param max_trials: Number of hyperparameter sets to try
    :param epochs: Epochs per trial
    :return: (best_model, best_hyperparameters, training_history)
    """

    def build_model(hp):
        model = Sequential()
        model.add(LSTM(
            units=hp.Int('lstm_units_1', 32, 128, step=32),
            return_sequences=True,
            input_shape=(X_train.shape[1], X_train.shape[2])
        ))
        model.add(Dropout(hp.Float('dropout_1', 0.1, 0.5, step=0.1)))
        model.add(LSTM(
            units=hp.Int('lstm_units_2', 16, 64, step=16)
        ))
        model.add(Dropout(hp.Float('dropout_2', 0.1, 0.5, step=0.1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        return model

    tuner = kt.RandomSearch(
        build_model,
        objective='val_loss',
        max_trials=max_trials,
        executions_per_trial=1,
        directory='tuning_results',
        project_name='btc_lstm_tuning'
    )

    tuner.search(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, verbose=1)
    best_model = tuner.get_best_models(1)[0]
    best_hps = tuner.get_best_hyperparameters(1)[0]
    history = best_model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=20)

    return best_model, best_hps, history


# --------------------------------------------------------------------
# LSTM Model Builder
# --------------------------------------------------------------------

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense

def build_lstm_model(input_shape):
    """
    Builds and compiles a stacked LSTM model.

    :param input_shape: Tuple (timesteps, features)
    :return: Compiled Keras model
    """
    logger.info(f"Building LSTM model with input shape {input_shape}")

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# --------------------------------------------------------------------
# LSTM Model Training Function
# --------------------------------------------------------------------

from tensorflow.keras.callbacks import EarlyStopping

def train_lstm_model(model, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
    """
    Trains the LSTM model using early stopping.

    :param model: Compiled LSTM model
    :param X_train: Training sequences
    :param y_train: Training targets
    :param X_val: Validation sequences
    :param y_val: Validation targets
    :param epochs: Training epochs
    :param batch_size: Batch size
    :return: Tuple of (trained model, training history)
    """
    logger.info(f"Training LSTM model for {epochs} epochs with batch size {batch_size}")
    
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stop],
        verbose=1
    )
    logger.info("Model training complete.")
    return model, history

# --------------------------------------------------------------------
# Training Loss Plot
# --------------------------------------------------------------------

import matplotlib.pyplot as plt

def plot_training_loss(history):
    """
    Plots training and validation loss curves from Keras history object.

    :param history: Keras history object from model.fit()
    """
    logger.info("Plotting training and validation loss.")
    plt.figure(figsize=(10, 5))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Training & Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()
