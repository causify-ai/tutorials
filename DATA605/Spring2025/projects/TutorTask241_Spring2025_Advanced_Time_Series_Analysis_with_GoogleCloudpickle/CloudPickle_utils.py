import requests
import pandas as pd
import cloudpickle
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os # For getpid in multiprocessing task and cpu_count

# --- CoinGecko API Interaction ---
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

def fetch_bitcoin_price_history(days=1, currency='usd'):
    """
    Fetches Bitcoin price history for the last 'days' from CoinGecko API.
    For 'days=1', it fetches hourly data for the last 24 hours.
    For 'days > 1', it fetches daily data.
    """
    url = f"{COINGECKO_API_URL}/coins/bitcoin/market_chart"
    params = {
        'vs_currency': currency,
        'days': days,
        # CoinGecko automatically provides hourly data for 1 day,
        # daily data for up to 90 days if interval is not specified.
        # For days > 90, it's daily. We'll let CoinGecko decide the optimal interval based on days.
        # If explicit hourly/daily control beyond this is needed, 'interval' param can be added.
        # For this project, 'days=1' implicitly gives hourly for last 24h.
    }
    try:
        print(f"Fetching Bitcoin data from CoinGecko: days={days}, currency={currency}")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        
        prices = data.get('prices', [])
        if not prices:
            print("Warning: No price data received from CoinGecko.")
            return pd.DataFrame(columns=['timestamp', 'price'])
            
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        print(f"Successfully fetched {len(df)} data points.")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CoinGecko: {e}")
        return pd.DataFrame(columns=['timestamp', 'price']) # Return empty DataFrame on error
    except Exception as e:
        print(f"An unexpected error occurred during data fetching: {e}")
        return pd.DataFrame(columns=['timestamp', 'price'])

# --- Data Serialization Wrappers (using cloudpickle) ---

def serialize_object(obj, filename):
    """Serializes an object using cloudpickle."""
    try:
        with open(filename, 'wb') as f:
            cloudpickle.dump(obj, f)
        print(f"Object successfully serialized to {filename}")
    except Exception as e:
        print(f"Error serializing object to {filename}: {e}")

def deserialize_object(filename):
    """Deserializes an object using cloudpickle."""
    try:
        with open(filename, 'rb') as f:
            obj = cloudpickle.load(f)
        print(f"Object successfully deserialized from {filename}")
        return obj
    except FileNotFoundError:
        print(f"Error: Serialization file {filename} not found.")
        return None
    except Exception as e:
        print(f"Error deserializing object from {filename}: {e}")
        return None

# --- Time Series Analysis Functions ---

def calculate_moving_average(df, window_size):
    """
    Calculates the simple moving average for the 'price' column.
    Adds a new column 'sma_{window_size}' to the DataFrame.
    """
    if df is None or 'price' not in df.columns:
        print(f"Warning: Column 'price' not found in DataFrame or DataFrame is None. Cannot calculate SMA.")
        return df
    if df.empty:
        print("Warning: DataFrame is empty. Cannot calculate SMA.")
        df[f'sma_{window_size}'] = pd.Series(dtype='float64') # Add empty SMA column
        return df

    df_copy = df.copy() # Avoid SettingWithCopyWarning
    df_copy[f'sma_{window_size}'] = df_copy['price'].rolling(window=window_size, min_periods=1).mean()
    return df_copy

def simple_trend_analysis(df):
    """
    Performs a very simple trend analysis based on the slope of the price data.
    Compares the first and last price points.
    """
    if df is None or 'price' not in df.columns or len(df) < 2:
        return "Insufficient data for trend analysis"
    
    first_price = df['price'].iloc[0]
    last_price = df['price'].iloc[-1]
    
    # Calculate percentage change for a more normalized "slope" idea
    if first_price == 0: # Avoid division by zero
        change_percentage = float('inf') if last_price > 0 else 0
    else:
        change_percentage = ((last_price - first_price) / first_price) * 100

    if last_price > first_price:
        trend = "Uptrend"
    elif last_price < first_price:
        trend = "Downtrend"
    else:
        trend = "Sideways/Flat"
    return f"Simple Trend: {trend} (Change: {change_percentage:.2f}%)"


def plot_price_data(df, title="Bitcoin Price Analysis", columns_to_plot=None):
    """
    Plots the specified columns from the DataFrame and saves the plot to a file.
    Defaults to plotting 'price' and any 'sma_X' columns if columns_to_plot is None.
    """
    if df is None or df.empty:
        print("DataFrame is empty, cannot plot.")
        return None
        
    plt.figure(figsize=(14, 7))
    
    if columns_to_plot is None:
        columns_to_plot = ['price'] # Default to plotting only price
        # Automatically add SMA columns if they exist
        sma_cols = sorted([col for col in df.columns if col.startswith('sma_')])
        columns_to_plot.extend(sma_cols)

    plot_actually_happened = False
    for col in columns_to_plot:
        if col in df.columns and not df[col].isnull().all(): # Check if column exists and is not all NaNs
            plt.plot(df.index, df[col], label=col.replace('_', ' ').title())
            plot_actually_happened = True
        else:
            print(f"Warning: Column '{col}' not found or contains all NaNs in DataFrame. Skipping for plotting.")
            
    if not plot_actually_happened:
        print("No valid data columns found to plot.")
        plt.close() # Close the empty plot
        return None
            
    plt.title(title)
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)") # Assuming USD, can be made dynamic
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_filename = f"btc_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    try:
        plt.savefig(plot_filename)
        print(f"Plot successfully saved to {plot_filename}")
    except Exception as e:
        print(f"Error saving plot: {e}")
        plot_filename = None # Indicate failure
    finally:
        plt.close() # Close the plot to free memory
    return plot_filename


# --- Functions for Multiprocessing ---

def task_process_data_chunk(serialized_input_tuple):
    """
    A task function designed to be run in a separate process.
    It deserializes the data chunk and a processing function, applies the function, 
    and returns the serialized result.
    
    Args:
        serialized_input_tuple (tuple): A tuple containing:
            - serialized_data_chunk (bytes): cloudpickled DataFrame chunk.
            - serialized_processing_function (bytes): cloudpickled function.
            - args_for_function (tuple): Additional arguments for the processing function (e.g., window_size).
    
    Returns:
        bytes: cloudpickled result of the processing function, or None on error.
    """
    try:
        serialized_data_chunk, serialized_processing_function, args_for_function = serialized_input_tuple
        
        data_chunk_df = cloudpickle.loads(serialized_data_chunk)
        processing_function = cloudpickle.loads(serialized_processing_function)
        
        # print(f"Process {os.getpid()} working on a chunk of size {len(data_chunk_df)} with function {processing_function.__name__}")
        if data_chunk_df.empty:
            return cloudpickle.dumps(pd.DataFrame()) # Return serialized empty DataFrame

        # Call the processing function with the DataFrame chunk and other arguments
        result_df = processing_function(data_chunk_df.copy(), *args_for_function)
        return cloudpickle.dumps(result_df)
    except Exception as e:
        print(f"Error in process {os.getpid()} during task execution: {e}")
        # Return serialized None or empty DataFrame to signal error or no result
        return cloudpickle.dumps(None) 

if __name__ == '__main__':
    # Example usage of utility functions (for direct testing of this module)
    print("--- Testing BTC_Analysis_utils.py ---")

    # 1. Fetch data (last 24 hours, hourly)
    print("\n[Test] Fetching Bitcoin Data (last 24 hours)...")
    btc_df_hourly = fetch_bitcoin_price_history(days=1)
    if not btc_df_hourly.empty:
        print(btc_df_hourly.head())

        # Test plotting for hourly data
        plot_filename_hourly = plot_price_data(btc_df_hourly, title="BTC Price - Last 24 Hours (Hourly)")
        if plot_filename_hourly:
            print(f"Hourly data plot generated: {plot_filename_hourly}")
    else:
        print("Could not fetch hourly Bitcoin data for testing.")

    # 2. Fetch data (last 7 days, daily)
    print("\n[Test] Fetching Bitcoin Data (last 7 days)...")
    btc_df_daily = fetch_bitcoin_price_history(days=7)
    if not btc_df_daily.empty:
        print(btc_df_daily.head())

        # 3. Serialize the DataFrame
        print("\n[Test] Serializing and Deserializing DataFrame...")
        serialize_object(btc_df_daily, 'test_btc_data.pkl')
        loaded_btc_df = deserialize_object('test_btc_data.pkl')
        if loaded_btc_df is not None:
            print("DataFrame loaded successfully. Head:")
            print(loaded_btc_df.head())

        # 4. Time Series Analysis
        print("\n[Test] Time Series Analysis...")
        sma_window = 3 # 3-day SMA
        analyzed_df = calculate_moving_average(loaded_btc_df.copy() if loaded_btc_df is not None else btc_df_daily.copy(), window_size=sma_window)
        if analyzed_df is not None and not analyzed_df.empty:
            print(f"Data with {sma_window}-period SMA (head):")
            print(analyzed_df.head())

            trend = simple_trend_analysis(analyzed_df)
            print(f"Trend Analysis: {trend}")

            # 5. Plot data
            print("\n[Test] Plotting Analyzed Data...")
            plot_filename_daily = plot_price_data(analyzed_df, title=f"BTC Price & {sma_window}-period SMA (7 days)")
            if plot_filename_daily:
                print(f"Daily data plot generated: {plot_filename_daily}")
        else:
            print("Analysis could not be performed or resulted in empty DataFrame.")

        # 6. Test serialization of a function
        print("\n[Test] Serializing and Deserializing a Function...")
        serialized_sma_func_filename = 'test_sma_function.pkl'
        serialize_object(calculate_moving_average, serialized_sma_func_filename)
        
        deserialized_sma_func = deserialize_object(serialized_sma_func_filename)
        
        if deserialized_sma_func is not None:
            print("Function deserialized successfully.")
            # Test the deserialized function
            df_from_deserialized_func = deserialized_sma_func(btc_df_daily.copy(), 2) # 2-period SMA
            if df_from_deserialized_func is not None and not df_from_deserialized_func.empty:
                print("Data with SMA calculated by deserialized function (head):")
                print(df_from_deserialized_func.head())
            else:
                print("Deserialized function did not produce expected output.")
        else:
            print("Failed to deserialize function.")
    else:
        print("Could not fetch daily Bitcoin data for extended testing.")
    
    print("\n--- End of CloudPickle_utils.py tests ---")