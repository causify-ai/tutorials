# ml_integration.py
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from petastorm import make_batch_reader

class BitcoinPricePredictor:
    def __init__(self, data_path='file:///bitcoin_data'):
        self.data_path = data_path
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def load_and_prepare_data(self, look_back=60, test_size=0.2):
        """Load data and prepare for LSTM model"""
        # Load data using Petastorm
        with make_batch_reader(self.data_path) as reader:
            data = next(reader)
        
        prices = data['price_usd'].numpy()
        prices = prices.reshape(-1, 1)
        
        # Scale data
        scaled_data = self.scaler.fit_transform(prices)
        
        # Create dataset for LSTM
        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Split into train and test
        split = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        return X_train, X_test, y_train, y_test
    
    def build_lstm_model(self, look_back):
        """Build LSTM model for price prediction"""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(look_back, 1)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(50, return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train_and_evaluate(self, look_back=60, epochs=20, batch_size=32):
        """Train and evaluate the model"""
        X_train, X_test, y_train, y_test = self.load_and_prepare_data(look_back)
        
        model = self.build_lstm_model(look_back)
        model.fit(X_train, y_train, 
                 epochs=epochs, 
                 batch_size=batch_size,
                 validation_data=(X_test, y_test))
        
        # Make predictions
        train_predict = model.predict(X_train)
        test_predict = model.predict(X_test)
        
        # Inverse transform predictions
        train_predict = self.scaler.inverse_transform(train_predict)
        y_train = self.scaler.inverse_transform([y_train])
        test_predict = self.scaler.inverse_transform(test_predict)
        y_test = self.scaler.inverse_transform([y_test])
        
        # Calculate RMSE
        train_rmse = np.sqrt(mean_squared_error(y_train[0], train_predict[:,0]))
        test_rmse = np.sqrt(mean_squared_error(y_test[0], test_predict[:,0]))
        
        print(f'Train RMSE: {train_rmse:.2f}')
        print(f'Test RMSE: {test_rmse:.2f}')
        
        return model, train_predict, test_predict