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

def load_and_clean_csv(file_path: str, remove_anomalies=True, z_threshold=3.0):
    """
    Load, clean, and optionally remove anomalous data points from the Bitcoin dataset.

    :param file_path: Path to the CSV file
    :param remove_anomalies: Whether to apply anomaly filtering (based on z-score)
    :param z_threshold: Z-score threshold for anomaly removal
    :return: Cleaned DataFrame
    """
    logger.info(f"Loading dataset from {file_path}")

    df = pd.read_csv(file_path)
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], utc=True)
    df = df.sort_values('snapped_at')
    df.set_index('snapped_at', inplace=True)

    for col in ['price', 'market_cap', 'total_volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['price'])
    df['market_cap'] = df['market_cap'].fillna(method='ffill')
    df['total_volume'] = df['total_volume'].fillna(method='ffill')
    df = df[~df.index.duplicated(keep='last')]

    if remove_anomalies:
        from scipy.stats import zscore
        df['zscore'] = zscore(df['price'].fillna(method='ffill'))
        original_len = len(df)
        df = df[np.abs(df['zscore']) < z_threshold]
        df.drop(columns='zscore', inplace=True)
        logger.info(f"Removed {original_len - len(df)} anomalous rows based on z-score > {z_threshold}")

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
def technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical indicators to the DataFrame:
    - Returns
    - Simple Moving Averages (SMA)
    - Rolling Volatility
    - Lag features
    - Relative Strength Index (RSI)
    - Moving Average Convergence Divergence (MACD)
    - Bollinger Bands

    :param df: Cleaned DataFrame with 'price' column
    :return: Enriched DataFrame
    """
    logger.info("Adding extended technical features...")

    df['returns'] = df['price'].pct_change()

    # SMAs
    df['SMA_7'] = df['price'].rolling(window=7).mean()
    df['SMA_30'] = df['price'].rolling(window=30).mean()

    # Volatility
    df['volatility_7'] = df['price'].rolling(window=7).std()
    df['volatility_30'] = df['price'].rolling(window=30).std()

    # Lag
    df['lag_1day'] = df['price'].shift(1)

    # RSI
    delta = df['price'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI_14'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['price'].ewm(span=12, adjust=False).mean()
    ema26 = df['price'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    sma20 = df['price'].rolling(window=20).mean()
    std20 = df['price'].rolling(window=20).std()
    df['BB_upper'] = sma20 + (2 * std20)
    df['BB_lower'] = sma20 - (2 * std20)

    logger.info("Technical feature engineering complete.")
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
    Builds and compiles the tuned LSTM model using best-found hyperparameters:
    - LSTM(128) + Dropout(0.4)
    - LSTM(48)  + Dropout(0.2)
    - Dense(1)

    :param input_shape: Tuple (timesteps, features)
    :return: Compiled Keras model
    """
    logger.info(f"Building LSTM model with input shape {input_shape}")

    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=input_shape),
        Dropout(0.4),
        LSTM(48),
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
# Fine-Tune Pretrained LSTM Model (on latest window)
# --------------------------------------------------------------------

from tensorflow.keras.models import load_model

def fine_tune_model(model_path: str, X_recent, y_recent, epochs: int = 5, batch_size: int = 32):
    """
    Loads an existing model and fine-tunes it on the most recent data.

    :param model_path: Path to the saved model (.h5 file)
    :param X_recent: Recent input sequences
    :param y_recent: Corresponding targets
    :param epochs: Fine-tuning epochs
    :param batch_size: Batch size
    :return: The updated model
    """
    logger.info(f"Fine-tuning model at {model_path} on recent data...")

    model = load_model(model_path)
    model.fit(X_recent, y_recent, epochs=epochs, batch_size=batch_size, verbose=1)

    model.save(model_path)
    logger.info(" Model fine-tuned and saved.")
    
    return model


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

# --------------------------------------------------------------------
# Model Evaluation
# --------------------------------------------------------------------
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def evaluate_predictions(y_true_scaled, y_pred_scaled, scaler_y, plot=False):
    """
    Inverse transforms scaled predictions and evaluates using MAE, RMSE.

    :param y_true_scaled: True values (scaled)
    :param y_pred_scaled: Predicted values (scaled)
    :param scaler_y: Target scaler (MinMaxScaler)
    :param plot: Whether to plot actual vs predicted
    :return: Dict of MAE and RMSE
    """
    logger.info("Evaluating model predictions...")

    y_true = scaler_y.inverse_transform(y_true_scaled.reshape(-1, 1)).flatten()
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    logger.info(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}")

    if plot:
        plot_actual_vs_predicted(y_true, y_pred)

    return {"MAE": mae, "RMSE": rmse}

# --------------------------------------------------------------------
#  Plot Actual vs. Predicted
# --------------------------------------------------------------------
import matplotlib.pyplot as plt

def plot_actual_vs_predicted(y_true, y_pred):
    """
    Plot actual vs. predicted prices.

    :param y_true: Actual prices
    :param y_pred: Predicted prices
    """
    plt.figure(figsize=(12, 6))
    plt.plot(y_true, label='Actual')
    plt.plot(y_pred, label='Predicted')
    plt.title("Actual vs Predicted Bitcoin Prices")
    plt.xlabel("Time Step")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

# --------------------------------------------------------------------
# Next Price Prediction & Plotting
# --------------------------------------------------------------------

def predict_next_price(model, X_input, scaler_y, recent_prices=None, plot=True):
    """
    Predict the next Bitcoin price from the most recent input sequence and optionally plot it.

    :param model: Trained Keras LSTM model
    :param X_input: Last input sequence, shape (1, window_size, features)
    :param scaler_y: Scaler used to inverse transform the prediction
    :param recent_prices: Optional array of recent actual prices for plotting (length = window_size)
    :param plot: Whether to plot the prediction
    :return: Predicted price (float)
    """
    import matplotlib.pyplot as plt

    logger.info("Predicting next Bitcoin price using latest sequence...")
    
    # Make prediction
    y_pred_scaled = model.predict(X_input)
    y_pred = scaler_y.inverse_transform(y_pred_scaled)[0][0]

    if plot and recent_prices is not None:
        logger.info("Plotting recent prices with prediction...")
        plt.figure(figsize=(12, 6))
        plt.plot(range(len(recent_prices)), recent_prices, label="Past Prices")
        plt.plot(len(recent_prices), y_pred, 'ro', label="Predicted Next Price")
        plt.title("Bitcoin Price Forecast")
        plt.xlabel("Time Step")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        plt.show()

    logger.info(f"Predicted price: ${y_pred:,.2f}")
    return y_pred
