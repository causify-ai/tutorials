import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
import json

# Load previously collected BTC prices (from a file or stream output)
def load_data(file_path='btc_prices.json'):
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

# Fit ARIMA model and forecast
def run_arima_forecast(df, steps=10):
    model = ARIMA(df['price'], order=(3, 1, 2))  # You can tune this
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    
    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(df.index, df['price'], label='Historical')
    future_index = pd.date_range(df.index[-1], periods=steps+1, freq='10s')[1:]
    plt.plot(future_index, forecast, label='Forecast', linestyle='--')
    plt.title('Bitcoin Price Forecast (ARIMA)')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.tight_layout()
    plt.show()

# Entry point
if __name__ == "__main__":
    df = load_data()
    run_arima_forecast(df)
