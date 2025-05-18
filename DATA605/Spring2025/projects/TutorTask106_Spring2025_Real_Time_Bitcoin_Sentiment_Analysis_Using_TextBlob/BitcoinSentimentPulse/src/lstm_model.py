"""
LSTM-based model for Bitcoin price forecasting.

This module implements a Long Short-Term Memory (LSTM) neural network
for time series forecasting of Bitcoin prices, with optional
sentiment integration.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from typing import Dict, List, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitcoinLSTMModel:
    """
    LSTM-based model for Bitcoin price forecasting.
    
    Attributes:
        forecast_horizon (int): Number of days to forecast
        lookback_window (int): Number of past days to use for prediction
        hidden_units (int): Number of units in LSTM layer
        dropout_rate (float): Dropout rate for regularization
        learning_rate (float): Learning rate for Adam optimizer
        batch_size (int): Batch size for training
        epochs (int): Maximum number of epochs for training
        include_sentiment (bool): Whether to include sentiment features
        model (tf.keras.Model): The trained Keras model
    """
    
    def __init__(
        self,
        forecast_horizon: int = 7,
        lookback_window: int = 30,
        hidden_units: int = 64,
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001,
        batch_size: int = 32,
        epochs: int = 100,
        include_sentiment: bool = True
    ):
        """
        Initialize the BitcoinLSTMModel.
        
        Args:
            forecast_horizon (int): Number of days to forecast
            lookback_window (int): Number of past days to use for prediction
            hidden_units (int): Number of units in LSTM layer
            dropout_rate (float): Dropout rate for regularization
            learning_rate (float): Learning rate for Adam optimizer
            batch_size (int): Batch size for training
            epochs (int): Maximum number of epochs for training
            include_sentiment (bool): Whether to include sentiment features
        """
        self.forecast_horizon = forecast_horizon
        self.lookback_window = lookback_window
        self.hidden_units = hidden_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.include_sentiment = include_sentiment
        self.model = None
        self.scaler = None
        
        # Set TensorFlow logging level
        tf.get_logger().setLevel('ERROR')
        
        # Set seed for reproducibility
        tf.random.set_seed(42)
    
    def _create_sequences(self, data: pd.DataFrame, target_column: str = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create input sequences for LSTM model.
        
        Args:
            data (pd.DataFrame): DataFrame with time series data
            target_column (str): Name of target column (defaults to 'Close' or 'price')
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: X and y arrays for model training
        """
        X, y = [], []
        
        # Determine target column
        if target_column is None:
            target_column = 'Close' if 'Close' in data.columns else 'price'
        
        # Use the target column and optional features
        features = [target_column]
        if self.include_sentiment and 'sentiment_polarity' in data.columns:
            features.append('sentiment_polarity')
        
        # Add technical indicators if available
        for col in data.columns:
            if col.startswith('rsi_') or col.startswith('macd_') or col.startswith('bb_'):
                features.append(col)
        
        # Create sequences
        data_array = data[features].values
        
        for i in range(len(data) - self.lookback_window - self.forecast_horizon + 1):
            X.append(data_array[i:(i + self.lookback_window)])
            y.append(data_array[i + self.lookback_window:i + self.lookback_window + self.forecast_horizon, 0])
        
        return np.array(X), np.array(y)
    
    def _build_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """
        Build LSTM model architecture.
        
        Args:
            input_shape (Tuple[int, int]): Shape of input sequences (lookback_window, n_features)
            
        Returns:
            tf.keras.Model: Compiled Keras model
        """
        # Use Input layer as recommended
        inputs = tf.keras.Input(shape=input_shape)
        
        # First LSTM layer with return sequences for stacking
        x = LSTM(
            units=self.hidden_units,
            return_sequences=True
        )(inputs)
        x = Dropout(self.dropout_rate)(x)
        
        # Second LSTM layer
        x = LSTM(units=self.hidden_units)(x)
        x = Dropout(self.dropout_rate)(x)
        
        # Output layer
        outputs = Dense(units=self.forecast_horizon)(x)
        
        # Create model
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mean_squared_error'
        )
        
        return model
    
    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data for model training.
        
        Args:
            data (pd.DataFrame): Original data
            
        Returns:
            pd.DataFrame: Normalized data
        """
        from sklearn.preprocessing import MinMaxScaler
        
        # Create a copy of the data
        normalized_data = data.copy()
        
        # Determine price column
        price_column = 'Close' if 'Close' in data.columns else 'price'
        
        # Initialize scaler if not already done
        if self.scaler is None:
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            normalized_data[price_column] = self.scaler.fit_transform(data[[price_column]])
        else:
            normalized_data[price_column] = self.scaler.transform(data[[price_column]])
        
        # Normalize other numeric columns if they exist
        for col in normalized_data.columns:
            if col != price_column and pd.api.types.is_numeric_dtype(normalized_data[col]):
                if col.startswith('sentiment_'):
                    # Sentiment is already between -1 and 1, just rescale to 0-1
                    normalized_data[col] = (normalized_data[col] + 1) / 2
                else:
                    # For other technical indicators, use robust scaling
                    normalized_data[col] = (normalized_data[col] - normalized_data[col].min()) / \
                                           (normalized_data[col].max() - normalized_data[col].min() + 1e-10)
        
        return normalized_data
    
    def fit_and_forecast(self, data: pd.DataFrame, sentiment_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Fit the model and generate forecasts.
        
        Args:
            data (pd.DataFrame): DataFrame with Bitcoin price data
            sentiment_data (Optional[pd.DataFrame]): Optional DataFrame with sentiment features
            
        Returns:
            Dict[str, Any]: Dictionary with forecast results and evaluation metrics
        """
        try:
            # Prepare data
            df = data.copy()
            
            # Determine price column
            price_column = 'Close' if 'Close' in df.columns else 'price'
            
            # Add sentiment features if available and requested
            if sentiment_data is not None and self.include_sentiment:
                df = pd.merge(df, sentiment_data, how='left', left_index=True, right_index=True)
                df['sentiment_polarity'].fillna(0, inplace=True)
                logger.info("Integrated sentiment data into LSTM model")
            else:
                # Add dummy sentiment column for consistency
                df['sentiment_polarity'] = 0
                if self.include_sentiment:
                    logger.info("No sentiment data available, using zero-filled sentiment")
            
            # Normalize data
            normalized_df = self._normalize_data(df)
            
            # Create sequences
            X, y = self._create_sequences(normalized_df, target_column=price_column)
            
            if len(X) == 0 or len(y) == 0:
                logger.error("Failed to create valid sequences for LSTM model")
                raise ValueError("Insufficient data for the specified lookback window and forecast horizon")
            
            # Split data into training and validation sets (80/20)
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Build and compile model
            input_shape = (X.shape[1], X.shape[2])
            self.model = self._build_model(input_shape)
            
            # Implement early stopping
            early_stopping = EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_data=(X_val, y_val),
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Get the final loss values
            train_loss = history.history['loss'][-1]
            val_loss = history.history['val_loss'][-1]
            
            # Generate forecast
            forecast_input = X[-1].reshape(1, X.shape[1], X.shape[2])
            forecast_normalized = self.model.predict(forecast_input, verbose=0)[0]
            
            # Inverse transform the forecast
            forecast_reshaped = forecast_normalized.reshape(-1, 1)
            forecast = self.scaler.inverse_transform(forecast_reshaped).flatten()
            
            # Calculate confidence intervals (simple approach based on historical error)
            mse = val_loss
            rmse = np.sqrt(mse)
            confidence_intervals = [(forecast[i] - 1.96 * rmse, forecast[i] + 1.96 * rmse) 
                                    for i in range(len(forecast))]
            
            # Generate dates for the forecast
            last_date = df.index[-1]
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), 
                                          periods=self.forecast_horizon, freq='D')
            
            # Create a dataframe with the forecast
            forecast_df = pd.DataFrame({
                'Forecast': forecast,
                'Lower_CI': [ci[0] for ci in confidence_intervals],
                'Upper_CI': [ci[1] for ci in confidence_intervals],
            }, index=forecast_dates)
            
            # Calculate evaluation metrics
            metrics = {
                'train_loss': float(train_loss),
                'val_loss': float(val_loss),
                'rmse': float(rmse),
                'model_type': 'LSTM',
                'lookback_window': self.lookback_window,
                'forecast_horizon': self.forecast_horizon,
                'used_sentiment': self.include_sentiment and sentiment_data is not None
            }
            
            # Return results
            return {
                'forecast': forecast_df,
                'metrics': metrics,
                'history': {
                    'loss': history.history['loss'],
                    'val_loss': history.history['val_loss']
                },
                'used_sentiment': self.include_sentiment and sentiment_data is not None
            }
            
        except Exception as e:
            logger.error(f"Error in LSTM model: {str(e)}")
            # Fallback to empty forecast
            return {
                'forecast': pd.DataFrame(),
                'metrics': {'error': str(e)},
                'used_sentiment': False
            }

# Test code (remove in production)
if __name__ == "__main__":
    # Simple test with random data
    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Create synthetic data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    close_prices = np.random.normal(20000, 1000, 100) + np.linspace(0, 2000, 100)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Close': close_prices
    }, index=dates)
    
    # Initialize and test model
    model = BitcoinLSTMModel(
        forecast_horizon=7,
        lookback_window=14,
        hidden_units=32,
        include_sentiment=False
    )
    
    results = model.fit_and_forecast(df)
    print(results['forecast'])
    print(results['metrics'])