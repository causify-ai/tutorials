# price_predictor.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
import logging
import os
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class BitcoinPricePredictor:
    """LSTM-based price predictor for Bitcoin."""
    
    def __init__(self, model_path: str = "models/bitcoin_lstm.h5"):
        self.model_path = model_path
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.sequence_length = 60  # Number of previous days to use for prediction
        self.prediction_days = 30  # Maximum days to predict ahead
        
        # Create model directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
    def _prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM model."""
        # Make sure we have a price column
        if 'price' not in data.columns and 'close' in data.columns:
            data['price'] = data['close']
        elif 'price' not in data.columns:
            raise ValueError("No price or close column in data")
            
        # Extract price column and convert to numpy array
        prices = data['price'].values.reshape(-1, 1)
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(prices)
        
        X = []
        y = []
        
        # Create sequences of length sequence_length
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i, 0])
            y.append(scaled_data[i, 0])
            
        # Convert to numpy arrays and reshape for LSTM
        X = np.array(X)
        y = np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y
    
    def train(self, data: pd.DataFrame, epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """Train the LSTM model on historical data."""
        try:
            logger.info(f"Training LSTM model on {len(data)} records")
            
            # Prepare data
            X, y = self._prepare_data(data)
            
            # Split into training and validation sets (80/20)
            split = int(0.8 * len(X))
            X_train, X_val = X[:split], X[split:]
            y_train, y_val = y[:split], y[split:]
            
            # Build LSTM model
            model = Sequential()
            model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
            model.add(Dropout(0.2))
            model.add(LSTM(units=50, return_sequences=True))
            model.add(Dropout(0.2))
            model.add(LSTM(units=50))
            model.add(Dropout(0.2))
            model.add(Dense(units=1))
            
            # Compile model
            model.compile(optimizer='adam', loss='mean_squared_error')
            
            # Train model
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val, y_val),
                verbose=1
            )
            
            # Save model
            model.save(self.model_path)
            self.model = model
            self.save_model()
            
            return {
                "loss": history.history['loss'][-1],
                "val_loss": history.history['val_loss'][-1],
                "epochs": len(history.history['loss']),
                "model_path": self.model_path,
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            return {"error": str(e)}
    
    def save_model(self):
        """Save both the model and the scaler for future use."""
        try:
            # Save the LSTM model
            if self.model is not None:
                self.model.save(self.model_path)
                logger.info(f"Model saved to {self.model_path}")
                
            # Save the scaler
            scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
            with open(scaler_path, 'wb') as f:
                import pickle
                pickle.dump(self.scaler, f)
            logger.info(f"Scaler saved to {scaler_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_model(self) -> bool:
        """Load a pre-trained model and scaler if available."""
        if not os.path.exists(self.model_path):
            logger.warning(f"No pre-trained model found at {self.model_path}")
            return False
            
        try:
            # Load the Keras model
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"Loaded pre-trained model from {self.model_path}")
            
            # Load the scaler
            scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    import pickle
                    self.scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {scaler_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def predict_future(self, data: pd.DataFrame, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict future Bitcoin prices."""
        # Limit days_ahead to maximum prediction days
        days_ahead = min(days_ahead, self.prediction_days)
        
        if self.model is None:
            if not self.load_model():
                logger.error("No model available for prediction")
                return {"error": "No trained model available"}
                
        try:
            logger.info(f"Predicting Bitcoin price {days_ahead} days ahead")
            
            # Make sure we have a price column
            if 'price' not in data.columns and 'close' in data.columns:
                data['price'] = data['close']
            elif 'price' not in data.columns:
                return {"error": "No price or close column in data"}
                
            # Extract price column and convert to numpy array
            prices = data['price'].values.reshape(-1, 1)
            
            # Scale the data using the same scaler
            scaled_data = self.scaler.fit_transform(prices)
            
            # Create the input sequence for prediction
            # We use the most recent sequence_length days for input
            input_sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)
            
            # Initialize prediction array
            predicted_prices = []
            current_sequence = input_sequence[0]
            
            # Predict one day at a time, updating the sequence each time
            for _ in range(days_ahead):
                current_batch = current_sequence.reshape(1, self.sequence_length, 1)
                predicted_price = self.model.predict(current_batch, verbose=0)[0][0]
                predicted_prices.append(predicted_price)
                current_sequence = np.append(current_sequence[1:], predicted_price)
            
            # Inverse transform predictions to actual prices
            predicted_prices = self.scaler.inverse_transform(
                np.array(predicted_prices).reshape(-1, 1)
            ).flatten()
            
            # Create result dictionary
            current_price = data['price'].iloc[-1]
            latest_date = data['date'].iloc[-1] if 'date' in data.columns else pd.Timestamp.now()
            
            # Generate future dates
            future_dates = []
            for i in range(1, days_ahead + 1):
                if isinstance(latest_date, pd.Timestamp):
                    date = latest_date + pd.Timedelta(days=i)
                else:
                    date = latest_date + timedelta(days=i)
                future_dates.append(date.strftime('%Y-%m-%d'))
                
            return {
                "current_price": current_price,
                "current_date": latest_date.strftime('%Y-%m-%d') if hasattr(latest_date, 'strftime') else str(latest_date),
                "predicted_prices": predicted_prices.tolist(),
                "predicted_dates": future_dates,
                "days_ahead": days_ahead,
                "expected_price_after_period": predicted_prices[-1],
                "predicted_change_percent": ((predicted_prices[-1] / current_price) - 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Error predicting future prices: {e}")
            return {"error": str(e)}
