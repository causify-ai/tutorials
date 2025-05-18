#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_directories():
    directories = [
        "data",
        "data/bitcoin",
        "forecasts",
        "evaluation",
        "tfx_pipeline_output",
        "tfx_pipeline_output/bitcoin_price_pipeline"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def create_dummy_data():
    data_path = "data/bitcoin/bitcoin_prices.csv"
    if os.path.exists(data_path):
        print(f"Data file already exists at: {data_path}")
        return

    sys.path.append(os.getcwd())
    try:
        from tf_bitcoin_utils import fetch_bitcoin_prices
        print("Fetching Bitcoin prices from API...")
        data = fetch_bitcoin_prices(days=30)
        data.to_csv(data_path, index=False)
        print(f"Saved Bitcoin price data with {len(data)} records")
        return
    except Exception as e:
        print(f"API fetch failed: {e}")
        print("Creating dummy data...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')

    base_price = 40000
    noise = np.random.normal(0, 1000, size=len(dates))
    trend = np.linspace(0, 5000, num=len(dates))
    prices = base_price + trend + noise

    dummy_data = pd.DataFrame({
        'timestamp': dates,
        'price': prices,
        'hour': dates.hour,
        'day_of_week': dates.dayofweek,
        'price_change': pd.Series(prices).pct_change().fillna(0),
        'rolling_mean_24h': pd.Series(prices).rolling(window=24).mean().bfill()
    })

    dummy_data.to_csv(data_path, index=False)
    print(f"Created dummy Bitcoin price data with {len(dummy_data)} records")

def create_dummy_forecast():
    forecast_dir = "forecasts"
    existing_forecasts = [f for f in os.listdir(forecast_dir) if f.endswith('.csv') or f.endswith('.png')]
    if existing_forecasts:
        print(f"Forecast files already exist: {existing_forecasts[:2]}")
        return

    print("Creating dummy forecast files...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    start_date = datetime.now() + timedelta(hours=1)
    end_date = datetime.now() + timedelta(days=7)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')

    base_price = 45000
    noise = np.random.normal(0, 500, size=len(dates))
    trend = np.linspace(0, 2000, num=len(dates))
    forecast_prices = base_price + trend + noise

    forecast_data = pd.DataFrame({
        'timestamp': dates,
        'predicted_price': forecast_prices
    })

    csv_path = f"{forecast_dir}/bitcoin_forecast_{timestamp}.csv"
    forecast_data.to_csv(csv_path, index=False)
    print(f"Created dummy forecast CSV: {csv_path}")

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(forecast_data['timestamp'], forecast_data['predicted_price'])
        plt.title('Bitcoin Price Forecast (Dummy Data)')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.grid(True)
        png_path = f"{forecast_dir}/bitcoin_forecast_{timestamp}.png"
        plt.savefig(png_path)
        plt.close()
        print(f"Created dummy forecast visualization: {png_path}")
    except Exception as e:
        print(f"Could not create forecast visualization: {e}")

def main():
    print("\n Bitcoin Price Forecasting System Setup \n")
    create_directories()
    create_dummy_data()
    create_dummy_forecast()
    print("\nSetup completed successfully!")

if __name__ == "__main__":
    main()
