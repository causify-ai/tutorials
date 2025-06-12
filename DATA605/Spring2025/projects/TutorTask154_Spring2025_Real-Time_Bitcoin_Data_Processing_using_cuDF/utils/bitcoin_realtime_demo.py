#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bitcoin Real-Time Analysis Demo with cuDF

This is a user-friendly demo script for analyzing Bitcoin price data using NVIDIA's cuDF
library for GPU-accelerated data processing. It provides an interactive experience
with prompts and clear explanations of what's happening at each step.

Usage:
    python bitcoin_realtime_demo.py

Author: Your Name
Date: 2025
"""

import os
import sys
import time
import cudf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import utility functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cudf_utils import (
    fetch_bitcoin_price, fetch_historical_data, add_to_dataframe,
    compute_moving_averages, compute_volatility, compute_rate_of_change,
    compute_rsi, simulate_realtime, plot_bitcoin_data,
    save_to_csv, load_from_csv, fetch_and_analyze_bitcoin
)

def print_header(title):
    """Print a formatted header for each section"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def check_cuda():
    """Check if CUDA is available and print GPU information"""
    try:
        import cupy as cp
        print("\n[SUCCESS] CUDA is available! Using GPU acceleration with cuDF.")
        
        # Get GPU information
        gpu_info = cp.cuda.runtime.getDeviceProperties(0)
        print(f"[INFO] GPU Device: {gpu_info['name'].decode()}")
        print(f"[INFO] CUDA Compute Capability: {gpu_info['major']}.{gpu_info['minor']}")
        print(f"[INFO] Total Memory: {gpu_info['totalGlobalMem'] / (1024**3):.2f} GB")
        
        return True
    except ImportError:
        print("\n[WARNING] CuPy not found. Make sure CUDA is properly configured for GPU acceleration.")
        return False
    except Exception as e:
        print(f"\n[WARNING] Error initializing CUDA: {e}")
        return False

def check_api_key():
    """Check if the CoinGecko API key is available"""
    api_key = os.getenv("COINGECKO_API_KEY")
    if api_key:
        masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "****"
        print(f"\n[API KEY] CoinGecko API key detected: {masked_key}")
        print("   Using API key for higher rate limits")
        return True
    else:
        print("\n[WARNING] CoinGecko API key not found. Using public API with lower rate limits.")
        print("   For higher rate limits, add your API key to .env file as COINGECKO_API_KEY")
        return False

def interactive_demo():
    """Run the interactive Bitcoin data analysis demo"""
    print_header("Bitcoin Real-Time Analysis Demo with NVIDIA cuDF")
    
    print("Welcome to the Bitcoin Data Analysis Demo using GPU-accelerated cuDF!")
    print("This demo will show you how to analyze Bitcoin price data using NVIDIA GPUs.\n")
    
    # Check CUDA availability
    has_cuda = check_cuda()
    
    # Check API key
    has_api_key = check_api_key()
    
    # Prompt user for analysis type
    print("\n[MENU] Choose an analysis type:")
    print("1. Historical Analysis (fetch and analyze past Bitcoin data)")
    print("2. Real-Time Analysis (collect and analyze live Bitcoin prices)")
    print("3. Combined Analysis (historical + real-time data)")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= 3:
                break
            else:
                print("[ERROR] Please enter a number between 1 and 3.")
        except ValueError:
            print("[ERROR] Please enter a valid number.")
    
    # Historical Analysis
    if choice in [1, 3]:
        print_header("Historical Bitcoin Data Analysis")
        
        # Ask for time period
        while True:
            try:
                days = int(input("Enter number of days of historical data to analyze (7-365): "))
                if 7 <= days <= 365:
                    break
                else:
                    print("[ERROR] Please enter a number between 7 and 365.")
            except ValueError:
                print("[ERROR] Please enter a valid number.")
        
        # Fetch and process historical data
        print(f"\n[FETCHING] Fetching {days} days of historical Bitcoin price data...")
        
        # Start timing
        start_time = time.time()
        
        # Fetch data
        historical_data = fetch_historical_data(days=days)
        
        if historical_data is None or len(historical_data) == 0:
            print("[ERROR] Failed to fetch historical data. Please check your internet connection and try again.")
            return
        
        fetch_time = time.time() - start_time
        print(f"[SUCCESS] Successfully fetched {len(historical_data)} historical data points in {fetch_time:.2f} seconds.")
        print(f"[DATE RANGE] Date range: {historical_data['timestamp'].min()} to {historical_data['timestamp'].max()}")
        print(f"[PRICE RANGE] Price range: ${historical_data['price'].min():.2f} to ${historical_data['price'].max():.2f}")
        
        # Process historical data
        print("\n[PROCESSING] Computing technical indicators...")
        start_time = time.time()
        
        historical_data = compute_moving_averages(historical_data, windows=[7, 20, 50, 200])
        historical_data = compute_volatility(historical_data, window=20)
        historical_data = compute_rate_of_change(historical_data, periods=[1, 7, 30])
        historical_data = compute_rsi(historical_data, window=14)
        
        process_time = time.time() - start_time
        print(f"[SUCCESS] Finished computing indicators in {process_time:.2f} seconds.")
        
        # Visualize historical data
        print("\n[VISUALIZATION] Generating visualization of historical data...")
        fig_historical = plot_bitcoin_data(historical_data, title=f"{days}-Day Bitcoin Price Analysis with cuDF")
        fig_historical.show()
        
        # Save historical data
        save_file = input("\nWould you like to save the historical data to CSV? (y/n): ").lower()
        if save_file == 'y':
            filename = f"historical_bitcoin_{days}days.csv"
            save_to_csv(historical_data, filename=filename)
            print(f"[SUCCESS] Data saved to {filename}")
    
    # Real-Time Analysis
    if choice in [2, 3]:
        print_header("Real-Time Bitcoin Data Analysis")
        
        # Ask for parameters
        while True:
            try:
                points = int(input("Enter number of data points to collect (5-50): "))
                if 5 <= points <= 50:
                    break
                else:
                    print("[ERROR] Please enter a number between 5 and 50.")
            except ValueError:
                print("[ERROR] Please enter a valid number.")
        
        while True:
            try:
                interval = int(input("Enter seconds between data points (1-10): "))
                if 1 <= interval <= 10:
                    break
                else:
                    print("[ERROR] Please enter a number between 1 and 10.")
            except ValueError:
                print("[ERROR] Please enter a valid number.")
        
        # Collect real-time data
        print(f"\n[COLLECTING] Collecting {points} real-time Bitcoin price data points with {interval} second intervals...")
        print(f"[TIME] This will take approximately {points * interval} seconds. Please wait...")
        
        # Collect data
        realtime_data = simulate_realtime(interval_seconds=interval, num_points=points)
        
        if realtime_data is None or len(realtime_data) == 0:
            print("[ERROR] Failed to collect real-time data. Please check your internet connection and try again.")
            return
        
        print(f"[SUCCESS] Successfully collected {len(realtime_data)} real-time data points.")
        
        # Process real-time data
        print("\n[PROCESSING] Computing technical indicators...")
        
        # Adjust window sizes based on available data points
        window_sizes = [min(3, len(realtime_data)-1), min(5, len(realtime_data)-1)]
        window_sizes = [w for w in window_sizes if w > 0]
        
        if window_sizes:
            realtime_data = compute_moving_averages(realtime_data, windows=window_sizes)
            realtime_data = compute_volatility(realtime_data, window=window_sizes[0])
            realtime_data = compute_rate_of_change(realtime_data, periods=[1])
            
            print(f"[SUCCESS] Finished computing indicators.")
        else:
            print("[WARNING] Not enough data points for technical indicators.")
        
        # Visualize real-time data
        print("\n[VISUALIZATION] Generating visualization of real-time data...")
        fig_realtime = plot_bitcoin_data(realtime_data, title="Real-Time Bitcoin Price Analysis with cuDF")
        fig_realtime.show()
        
        # Save real-time data
        save_file = input("\nWould you like to save the real-time data to CSV? (y/n): ").lower()
        if save_file == 'y':
            filename = f"realtime_bitcoin_{points}points.csv"
            save_to_csv(realtime_data, filename=filename)
            print(f"[SUCCESS] Data saved to {filename}")
    
    # Combined Analysis
    if choice == 3 and 'historical_data' in locals() and 'realtime_data' in locals():
        print_header("Combined Historical and Real-Time Analysis")
        
        print("[COMBINING] Combining historical and real-time data...")
        
        # Ensure timestamp is datetime for concatenation
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'].to_pandas())
        realtime_data['timestamp'] = pd.to_datetime(realtime_data['timestamp'].to_pandas())
        
        # Combine the data
        combined_data = cudf.concat([historical_data, realtime_data], ignore_index=True)
        
        # Remove duplicates if any
        combined_data = combined_data.drop_duplicates(subset=['timestamp'], keep='last')
        
        # Sort by timestamp
        combined_data = combined_data.sort_values('timestamp')
        
        print(f"[SUCCESS] Combined data has {len(combined_data)} rows")
        
        # Visualize combined data
        print("\n[VISUALIZATION] Generating visualization of combined data...")
        fig_combined = plot_bitcoin_data(combined_data, title="Combined Historical and Real-Time Bitcoin Analysis with cuDF")
        fig_combined.show()
        
        # Save combined data
        save_file = input("\nWould you like to save the combined data to CSV? (y/n): ").lower()
        if save_file == 'y':
            filename = "combined_bitcoin_data.csv"
            save_to_csv(combined_data, filename=filename)
            print(f"[SUCCESS] Data saved to {filename}")
    
    print_header("Demo Complete")
    
    print("Thank you for using the Bitcoin Data Analysis Demo with NVIDIA cuDF!")
    print("Key Takeaways:")
    print("1. GPU-accelerated data processing with cuDF enables fast analysis of financial data")
    print("2. cuDF provides a pandas-like API but with GPU acceleration")
    print("3. Technical indicators and visualizations can be generated quickly even for large datasets")
    
    if not has_cuda:
        print("\n[NOTE] This demo would run much faster with a CUDA-enabled NVIDIA GPU.")
        print("   Consider running on hardware with GPU support for optimal performance.")
    
    print("\nFor more information, visit:")
    print("- RAPIDS cuDF: https://docs.rapids.ai/api/cudf/stable/")
    print("- Bitcoin APIs: https://www.coingecko.com/en/api/documentation")

if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Demo interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[GOODBYE] Thank you for using the Bitcoin Analysis Demo with cuDF!") 