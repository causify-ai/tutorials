#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bitcoin Real-Time Processor with cuDF

This script fetches and processes Bitcoin price data using NVIDIA's cuDF library 
for GPU-accelerated data analysis. It can operate in four modes:
- historical: Fetch and analyze historical data only
- realtime: Fetch and analyze real-time data only
- both: Fetch historical data and then append real-time data
- forecast: Fetch historical data, analyze it, and forecast future prices

Usage:
    python bitcoin_realtime_processor.py --mode historical --days 365
    python bitcoin_realtime_processor.py --mode realtime --interval 5 --points 30
    python bitcoin_realtime_processor.py --mode both --days 365 --interval 5 --points 10
    python bitcoin_realtime_processor.py --mode forecast --days 365 --forecast-days 30

Author: Your Name
Date: 2025
"""

import os
import sys
import time
import argparse
import cudf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import utility functions
from utils.cudf_utils import (
    fetch_bitcoin_price, fetch_historical_data, add_to_dataframe,
    compute_moving_averages, compute_volatility, compute_rate_of_change,
    compute_rsi, simulate_realtime, plot_bitcoin_data,
    save_to_csv, load_from_csv, fetch_and_analyze_bitcoin
)

def process_historical_data(days, output=None):
    """
    Process historical Bitcoin price data
    
    Args:
        days (int): Number of days of historical data to fetch
        output (str, optional): Output CSV filename
    
    Returns:
        cudf.DataFrame: Processed historical data
    """
    print(f"Fetching {days} days of historical Bitcoin price data...")
    
    # Fetch historical data
    gdf = fetch_historical_data(days=days)
    
    if gdf is None or len(gdf) == 0:
        print("Failed to fetch historical data.")
        return None
    
    print(f"Successfully fetched {len(gdf)} historical data points.")
    print(f"Date range: {gdf['timestamp'].min()} to {gdf['timestamp'].max()}")
    print(f"Price range: ${gdf['price'].min():.2f} to ${gdf['price'].max():.2f}")
    
    # Compute technical indicators
    print("Computing technical indicators...")
    gdf = compute_moving_averages(gdf, windows=[7, 20, 50, 200])
    gdf = compute_volatility(gdf, window=20)
    gdf = compute_rate_of_change(gdf, periods=[1, 7, 30])
    gdf = compute_rsi(gdf, window=14)
    
    # Save to CSV if output filename provided
    if output:
        save_to_csv(gdf, filename=output)
    
    return gdf

def process_realtime_data(interval, points, output=None):
    """
    Process real-time Bitcoin price data
    
    Args:
        interval (int): Seconds between API calls
        points (int): Number of data points to collect
        output (str, optional): Output CSV filename
    
    Returns:
        cudf.DataFrame: Processed real-time data
    """
    print(f"Collecting {points} real-time Bitcoin price data points with {interval} second intervals...")
    
    # Collect real-time data
    gdf = simulate_realtime(interval_seconds=interval, num_points=points)
    
    if gdf is None or len(gdf) == 0:
        print("Failed to collect real-time data.")
        return None
    
    print(f"Successfully collected {len(gdf)} real-time data points.")
    
    # Compute technical indicators (adjusted for smaller dataset)
    print("Computing technical indicators...")
    window_sizes = [min(3, len(gdf)-1), min(5, len(gdf)-1)]
    window_sizes = [w for w in window_sizes if w > 0]
    
    if window_sizes:
        gdf = compute_moving_averages(gdf, windows=window_sizes)
        gdf = compute_volatility(gdf, window=window_sizes[0])
        gdf = compute_rate_of_change(gdf, periods=[1])
    
    # Save to CSV if output filename provided
    if output:
        save_to_csv(gdf, filename=output)
    
    return gdf

def forecast_bitcoin_prices(historical_data, forecast_days=30, output=None):
    """
    Forecast Bitcoin prices using historical data
    
    Args:
        historical_data (cudf.DataFrame): Historical Bitcoin price data
        forecast_days (int): Number of days to forecast
        output (str, optional): Output CSV filename
    
    Returns:
        tuple: (historical_data, forecast_data) as pandas DataFrames
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    
    print(f"Forecasting Bitcoin prices for the next {forecast_days} days...")
    
    if historical_data is None or len(historical_data) < 30:
        print("Insufficient historical data for forecasting. Need at least 30 data points.")
        return None, None
    
    # Convert to pandas for forecasting
    df = historical_data.to_pandas()
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    
    # Keep only the price column for basic forecasting
    price_series = df['price']
    
    # Create features for regression (using lag features)
    X = np.column_stack([
        price_series.shift(1).values[30:],
        price_series.shift(7).values[30:],
        price_series.shift(14).values[30:],
        price_series.shift(30).values[30:],
        price_series.rolling(7).mean().shift(1).values[30:],
        price_series.rolling(14).mean().shift(1).values[30:],
        price_series.rolling(30).mean().shift(1).values[30:],
        price_series.rolling(7).std().shift(1).values[30:],
        price_series.pct_change(periods=1).shift(1).values[30:],
        price_series.pct_change(periods=7).shift(1).values[30:],
    ])
    
    # Target variable
    y = price_series.values[30:]
    
    # Remove NaN rows
    valid_indices = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
    X_clean = X[valid_indices]
    y_clean = y[valid_indices]
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)
    
    # Train a linear regression model
    model = LinearRegression()
    model.fit(X_scaled, y_clean)
    
    print("Model trained. Generating forecast...")
    
    # Prepare data for forecasting
    forecast_horizon = forecast_days
    forecast_dates = [df.index[-1] + timedelta(days=i+1) for i in range(forecast_horizon)]
    
    # Initialize with known values
    forecast_values = []
    forecast_df = price_series.copy()
    
    # Step-by-step forecast
    for i in range(forecast_horizon):
        # Get the latest data point
        latest_price = forecast_df.iloc[-1] if i == 0 else forecast_values[-1]
        latest_price_lag1 = forecast_df.iloc[-1]
        latest_price_lag7 = forecast_df.iloc[-7] if len(forecast_df) > 7 else forecast_df.iloc[0]
        latest_price_lag14 = forecast_df.iloc[-14] if len(forecast_df) > 14 else forecast_df.iloc[0]
        latest_price_lag30 = forecast_df.iloc[-30] if len(forecast_df) > 30 else forecast_df.iloc[0]
        
        # Calculate rolling stats
        if i == 0:
            ma7 = forecast_df.rolling(7).mean().iloc[-1]
            ma14 = forecast_df.rolling(14).mean().iloc[-1]
            ma30 = forecast_df.rolling(30).mean().iloc[-1]
            std7 = forecast_df.rolling(7).std().iloc[-1]
            pct1 = forecast_df.pct_change(periods=1).iloc[-1]
            pct7 = forecast_df.pct_change(periods=7).iloc[-1]
        else:
            # Append the latest prediction to the series
            temp_series = pd.concat([forecast_df, pd.Series([forecast_values[-1]], index=[forecast_dates[i-1]])])
            ma7 = temp_series.rolling(7).mean().iloc[-1]
            ma14 = temp_series.rolling(14).mean().iloc[-1]
            ma30 = temp_series.rolling(30).mean().iloc[-1]
            std7 = temp_series.rolling(7).std().iloc[-1]
            pct1 = (temp_series.iloc[-1] / temp_series.iloc[-2]) - 1 if len(temp_series) > 1 else 0
            pct7 = (temp_series.iloc[-1] / temp_series.iloc[-7]) - 1 if len(temp_series) > 7 else 0
        
        # Create feature vector
        X_forecast = np.array([[
            latest_price_lag1,
            latest_price_lag7,
            latest_price_lag14,
            latest_price_lag30,
            ma7,
            ma14,
            ma30,
            std7,
            pct1,
            pct7
        ]])
        
        # Scale the features
        X_forecast_scaled = scaler.transform(X_forecast)
        
        # Make prediction
        forecast_price = model.predict(X_forecast_scaled)[0]
        forecast_values.append(forecast_price)
    
    # Create DataFrame with forecasted values
    forecast_result = pd.DataFrame({'price': forecast_values}, index=forecast_dates)
    
    # Add confidence intervals (simple approach using historical volatility)
    volatility = df['price'].pct_change().std() * np.sqrt(forecast_horizon)
    forecast_result['lower_bound'] = forecast_result['price'] * (1 - volatility * 1.96)
    forecast_result['upper_bound'] = forecast_result['price'] * (1 + volatility * 1.96)
    
    print(f"30-day forecast generated with confidence intervals.")
    
    # Save to CSV if output filename provided
    if output:
        forecast_result.to_csv(output)
        print(f"Forecast saved to {output}")
    
    return df, forecast_result

def main():
    """Main function to process Bitcoin data based on command line arguments"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process Bitcoin price data with cuDF')
    parser.add_argument('--mode', type=str, choices=['historical', 'realtime', 'both', 'forecast'], 
                        default='both', help='Processing mode')
    parser.add_argument('--days', type=int, default=365, 
                        help='Number of days of historical data to fetch')
    parser.add_argument('--interval', type=int, default=30, 
                        help='Seconds between real-time API calls')
    parser.add_argument('--points', type=int, default=20, 
                        help='Number of real-time data points to collect')
    parser.add_argument('--forecast-days', type=int, default=30,
                        help='Number of days to forecast')
    parser.add_argument('--output', type=str, default=None, 
                        help='Output CSV filename')
    parser.add_argument('--no-plot', action='store_true',
                        help='Disable interactive plotting')
    args = parser.parse_args()
    
    # Process data based on mode
    if args.mode in ['historical', 'both', 'forecast']:
        historical_data = process_historical_data(
            days=args.days, 
            output=f"historical_bitcoin_{args.days}days.csv" if args.output is None else args.output
        )
        
        if historical_data is not None and not args.no_plot and args.mode != 'forecast':
            # Visualize historical data
            fig = plot_bitcoin_data(historical_data, title=f"{args.days}-Day Bitcoin Price Analysis with cuDF")
            fig.show()
    
    if args.mode in ['realtime', 'both']:
        realtime_data = process_realtime_data(
            interval=args.interval,
            points=args.points,
            output=f"realtime_bitcoin_{args.points}points.csv" if args.output is None else args.output
        )
        
        if realtime_data is not None and not args.no_plot:
            # Visualize real-time data
            fig = plot_bitcoin_data(realtime_data, title="Real-Time Bitcoin Price Analysis with cuDF")
            fig.show()
    
    # If forecast mode
    if args.mode == 'forecast' and historical_data is not None:
        historical_df, forecast_df = forecast_bitcoin_prices(
            historical_data=historical_data,
            forecast_days=args.forecast_days,
            output=f"bitcoin_forecast_{args.forecast_days}days.csv" if args.output is None else args.output
        )
        
        if historical_df is not None and forecast_df is not None and not args.no_plot:
            # Visualize forecast
            print('plot_forecast is unavailable. Please restore utils/plot_forecast.py if you need forecast plots.')
            
            # Calculate key stats
            last_price = historical_df['price'].iloc[-1]
            forecast_end_price = forecast_df['price'].iloc[-1]
            price_change = forecast_end_price - last_price
            price_change_pct = (price_change / last_price) * 100
            
            print(f"Current Bitcoin price: ${last_price:.2f}")
            print(f"Forecasted price ({args.forecast_days} days): ${forecast_end_price:.2f}")
            print(f"Forecasted change: ${price_change:.2f} ({price_change_pct:.2f}%)")
            print(f"95% Confidence interval: ${forecast_df['lower_bound'].iloc[-1]:.2f} to ${forecast_df['upper_bound'].iloc[-1]:.2f}")
    
    # If both modes, combine the data
    if args.mode == 'both' and historical_data is not None and realtime_data is not None:
        print("Combining historical and real-time data...")
        
        # Ensure timestamp is datetime for concatenation
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'].to_pandas())
        realtime_data['timestamp'] = pd.to_datetime(realtime_data['timestamp'].to_pandas())
        
        # Combine the data
        combined_data = cudf.concat([historical_data, realtime_data], ignore_index=True)
        
        # Remove duplicates if any
        combined_data = combined_data.drop_duplicates(subset=['timestamp'], keep='last')
        
        # Sort by timestamp
        combined_data = combined_data.sort_values('timestamp')
        
        print(f"Combined data has {len(combined_data)} rows")
        
        # Save combined data
        if args.output:
            save_to_csv(combined_data, filename=f"combined_{args.output}")
        else:
            save_to_csv(combined_data, filename=f"combined_bitcoin_data.csv")
        
        if not args.no_plot:
            # Visualize combined data
            fig = plot_bitcoin_data(combined_data, title="Combined Historical and Real-Time Bitcoin Analysis with cuDF")
            fig.show()

if __name__ == "__main__":
    # Check if CUDA is available
    try:
        import cupy
        print("CUDA is available. Using GPU acceleration with cuDF.")
    except ImportError:
        print("WARNING: CuPy not found. Make sure CUDA is properly configured for GPU acceleration.")
    except Exception as e:
        print(f"WARNING: Error initializing CUDA: {e}")
    
    # Check API key status
    api_key = os.getenv("COINGECKO_API_KEY")
    if api_key:
        masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "****"
        print(f"CoinGecko API key detected: {masked_key}")
        print("Using API key for higher rate limits")
    else:
        print("WARNING: CoinGecko API key not found. Using public API with lower rate limits.")
        print("For higher rate limits, add your API key to .env file as COINGECKO_API_KEY")
    
    main() 