import numpy as np
import pandas as pd
from datetime import timedelta

# Auto ARIMA
from pmdarima import auto_arima

# LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

from src.utils_analyzer import extrapolate_future_exog

def run_auto_arima_forecast(merged_data, forecast_hours=24):
    """
    Forecast Bitcoin price using auto_arima (pmdarima) on an hourly basis.
    Returns:
        forecast_results: DataFrame with actual and predicted values for the test set
        future_forecast: DataFrame with future forecasted values
    """
    merged_data = merged_data.copy()
    merged_data['date'] = pd.to_datetime(merged_data['date'])
    merged_data = merged_data.sort_values('date')
    merged_data = merged_data.drop_duplicates(subset='date', keep='last')
    if not (merged_data['date'].diff().dt.total_seconds().dropna() == 3600).all():
        merged_data = merged_data.set_index('date').resample('h').ffill().reset_index()

    # Train-test split
    test_size = forecast_hours
    train_size = max(int(len(merged_data) * 0.8), len(merged_data) - test_size)
    train_data = merged_data.iloc[:train_size]
    test_data = merged_data.iloc[train_size:]

    y_train = train_data['close_price'].values
    y_test = test_data['close_price'].values
    X_train = train_data[['avg_polarity', 'polarity_volatility']].values
    X_test = test_data[['avg_polarity', 'polarity_volatility']].values

    # Fit model
    model = auto_arima(y_train, exogenous=X_train, seasonal=False, trace=False, error_action='ignore', suppress_warnings=True)
    predictions = model.predict(n_periods=len(y_test), exogenous=X_test)

    # Error metrics
    from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
    mape = mean_absolute_percentage_error(y_test, predictions) * 100
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    forecast_results = pd.DataFrame({
        'date': test_data['date'].values,
        'actual_price': y_test,
        'predicted_price': predictions,
        'avg_polarity': test_data['avg_polarity'].values
    })
    forecast_results['upper_ci'] = forecast_results['predicted_price'] + 1.96 * rmse
    forecast_results['lower_ci'] = forecast_results['predicted_price'] - 1.96 * rmse
    forecast_results['mape'] = mape
    forecast_results['rmse'] = rmse

    # Future forecast
    future_exog = extrapolate_future_exog(merged_data, forecast_hours=forecast_hours, window=3)
    exog_cols = ['avg_polarity', 'polarity_volatility']
    future_exog = np.clip(future_exog, a_min=merged_data[exog_cols].quantile(0.25).values, a_max=None)
    future_predictions = model.predict(n_periods=forecast_hours, exogenous=future_exog)
    last_date = pd.to_datetime(merged_data['date'].iloc[-1])
    dates = pd.date_range(start=last_date + timedelta(hours=1), periods=forecast_hours, freq='h')
    future_forecast = pd.DataFrame({'date': dates, 'predicted_price': future_predictions})

    return forecast_results, future_forecast

def run_lstm_forecast(merged_data, forecast_hours=24, sequence_length=24):
    """
    Forecast Bitcoin price using LSTM on an hourly basis.
    Returns:
        forecast_results: DataFrame with actual and predicted values for the test set
        future_forecast: DataFrame with future forecasted values
    """
    merged_data = merged_data.copy()
    merged_data['date'] = pd.to_datetime(merged_data['date'])
    merged_data = merged_data.sort_values('date')
    merged_data = merged_data.drop_duplicates(subset='date', keep='last')
    if not (merged_data['date'].diff().dt.total_seconds().dropna() == 3600).all():
        merged_data = merged_data.set_index('date').resample('h').ffill().reset_index()

    scaler = MinMaxScaler()
    features = merged_data[['close_price', 'avg_polarity', 'polarity_volatility']].values
    scaled = scaler.fit_transform(features)

    # Create sequences
    X, y = [], []
    for i in range(len(scaled) - sequence_length):
        X.append(scaled[i:i+sequence_length])
        y.append(scaled[i+sequence_length, 0])
    X, y = np.array(X), np.array(y)

    # Train-test split
    test_size = forecast_hours
    split = max(int(len(X) * 0.8), len(X) - test_size)
    X_train, y_train = X[:split], y[:split]
    X_test, y_test = X[split:], y[split:]

    # Build LSTM model
    model = Sequential([
        LSTM(50, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_test, y_test), verbose=0)

    # Predict on test set
    test_preds = model.predict(X_test, verbose=0).flatten()
    from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
    mape = mean_absolute_percentage_error(y_test, test_preds) * 100
    rmse = np.sqrt(mean_squared_error(y_test, test_preds))

    test_dates = merged_data['date'].iloc[sequence_length+split:sequence_length+split+len(y_test)].values
    test_avg_polarity = merged_data['avg_polarity'].iloc[sequence_length+split:sequence_length+split+len(y_test)].values
    forecast_results = pd.DataFrame({
        'date': test_dates,
        'actual_price': scaler.inverse_transform(np.c_[y_test, np.tile(scaled[-1, 1:], (len(y_test), 1))])[:, 0],
        'predicted_price': scaler.inverse_transform(np.c_[test_preds, np.tile(scaled[-1, 1:], (len(test_preds), 1))])[:, 0],
        'avg_polarity': test_avg_polarity
    })
    forecast_results['upper_ci'] = forecast_results['predicted_price'] + 1.96 * rmse
    forecast_results['lower_ci'] = forecast_results['predicted_price'] - 1.96 * rmse
    forecast_results['mape'] = mape
    forecast_results['rmse'] = rmse

    # Future forecast
    last_seq = X[-1]
    preds = []
    current_seq = last_seq.copy()
    for _ in range(forecast_hours):
        pred = model.predict(current_seq[np.newaxis, :, :], verbose=0)[0, 0]
        preds.append(pred)
        # Use last known sentiment for future
        new_row = np.array([pred, scaled[-1, 1], scaled[-1, 2]])
        current_seq = np.vstack([current_seq[1:], new_row])
    preds_full = np.zeros((len(preds), features.shape[1]))
    preds_full[:, 0] = preds
    preds_full[:, 1:] = scaled[-1, 1:]
    preds_inv = scaler.inverse_transform(preds_full)[:, 0]
    last_date = pd.to_datetime(merged_data['date'].iloc[-1])
    dates = pd.date_range(start=last_date + timedelta(hours=1), periods=forecast_hours, freq='h')
    future_forecast = pd.DataFrame({'date': dates, 'predicted_price': preds_inv})

    return forecast_results, future_forecast 