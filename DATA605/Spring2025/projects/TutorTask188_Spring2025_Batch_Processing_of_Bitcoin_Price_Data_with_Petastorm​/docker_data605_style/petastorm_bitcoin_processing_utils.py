import requests
import time
import pandas as pd
import numpy as np
from datetime import datetime
import os
import pyarrow as pa
import pyarrow.parquet as pq
import matplotlib.pyplot as plt

from pyspark.sql import SparkSession
from petastorm.etl.dataset_metadata import materialize_dataset
from petastorm.codecs import ScalarCodec
from petastorm.unischema import Unischema, UnischemaField
from petastorm.reader import make_batch_reader

# Helper function to complete the project

# Define schema for Bitcoin price data
BitcoinSchema = Unischema('BitcoinSchema', [
    UnischemaField('timestamp', np.str_, (), ScalarCodec(np.str_), False),
    UnischemaField('price_usd', np.float32, (), ScalarCodec(np.float32), False),
    UnischemaField('market_cap', np.float64, (), ScalarCodec(np.float64), False),
    UnischemaField('price_change_24h', np.float32, (), ScalarCodec(np.float32), False),
])

# ==============================
# API Interaction Functions
# ==============================
def fetch_current_price(base_url):
    """Fetch current Bitcoin price in USD from CoinGecko"""
    endpoint = f"{base_url}/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_change': 'true'
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    
    return {
        'timestamp': datetime.now().isoformat(),
        'price_usd': data['bitcoin']['usd'],
        'market_cap': data['bitcoin']['usd_market_cap'],
        'price_change_24h': data['bitcoin']['usd_24h_change']
    }

# ==============================
# Data Saving Functions
# ==============================
def save_to_csv(df, output_dir, filename=None):
    """Save DataFrame to CSV"""
    if filename is None:
        filename = f"bitcoin_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, header=True)
    print(f"Data saved to {filepath}")
    return filepath

def save_to_parquet_arrow(df, output_path="file:///docker_data605_style/test_bitcoin_data/parquet"):
    """
    Save a Pandas DataFrame as a Parquet file readable by Petastorm (without Spark).
    
    Args:
        df (pd.DataFrame): The dataset to save.
        output_path (str): Parquet destination (can include 'file://' prefix).
    """
    # Strip file:// if present
    current_dir = os.getcwd()
    local_path = output_path.replace("file://",current_dir) if output_path.startswith("file://") else output_path

    # Create the directory if it doesn't exist
    os.makedirs(local_path, exist_ok=True)

    # Convert and save
    table = pa.Table.from_pandas(df)
    pq.write_table(table, os.path.join(local_path, "data.parquet"))

    print(f"======== Parquet file written to \n {local_path} ==========")



# ==============================
# Data Loading Functions
# ==============================
def load_all_csvs_from_folder(folder_path):
    """
    Load and concatenate all CSV files in a given folder into one DataFrame.

    Args:
        folder_path (str): Path to the folder containing CSV files.

    Returns:
        pd.DataFrame: Combined DataFrame of all CSVs.
    """
    abs_path = os.path.abspath(folder_path)
    files = os.listdir(abs_path)
    all_files = [f for f in files if f.endswith('.csv')]
    dataframes = []

    for file in all_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path)
            dataframes.append(df)
            # print(f"Loaded {file}")
        except Exception as e:
            print(f"Failed to load {file}: {e}")

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"Combined {len(dataframes)} CSV files.")
        return combined_df
    else:
        print("No CSV files loaded.")
        return pd.DataFrame()  # Return empty DataFrame


def load_petastorm_batches_to_df(parquet_path):
    """
    Reads a Petastorm-compatible Parquet directory and converts it to a single Pandas DataFrame.

    Args:
        parquet_path (str): Path in 'file:///...' format.

    Returns:
        pd.DataFrame: Combined DataFrame of all batches.
    """
    all_batches = []
    with make_batch_reader(parquet_path) as reader:
        for batch in reader:
            all_batches.append(pd.DataFrame(batch))
    return pd.concat(all_batches, ignore_index=True)



# ==============================
# Data Processing Function
# ==============================
import os
from petastorm.reader import make_batch_reader

def load_from_parquet(input_dir):
    """Load data from Parquet using Petastorm"""
    
    # Fix for local file paths with 'file://'
    if input_dir.startswith("file://"):
        path_part = input_dir[7:]
        local_path = os.path.abspath(path_part)
        url_path = f'file://{local_path.replace(os.sep, "/")}'  # Normalize slashes for Petastorm
    else:
        # Assume it's a plain path, convert to absolute and make it a file:// URL
        local_path = os.path.abspath(input_dir)
        url_path = f'file://{local_path.replace(os.sep, "/")}'

    print(f"Loading data from {url_path}...")
    
    # Read data
    with make_batch_reader(url_path) as reader:
        for batch in reader:
            yield batch



# ==============================
# Utility Functions 
# ==============================

def get_parquet_columns(parquet_file_path):
    """
    Returns the list of column names from a Parquet file using PyArrow.
    
    Args:
        parquet_file_path (str): Full path to the Parquet file (can include 'file://' or not).
    
    Returns:
        List[str]: Column names in the Parquet dataset.
    """
    if parquet_file_path.startswith("file://"):
        parquet_file_path = parquet_file_path.replace("file://", "")
    
    table = pq.read_table(parquet_file_path)
    return table.column_names


# ==============================
# Data Processing Functions
# ==============================
def prepare_bitcoin_df(df):
    required = ['timestamp', 'price_usd']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    # Clean and parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp', 'price_usd'], inplace=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    return df

def calculate_moving_average(df, window=7):
    df[f'ma_{window}'] = df['price_usd'].rolling(window=window).mean()
    return df

def calculate_volatility(df, window=7):
    df[f'volatility_{window}'] = df['price_usd'].pct_change().rolling(window=window).std()
    return df

def plot_price_trend(df):
    plt.figure(figsize=(12, 6))
    df['price_usd'].plot(title='Bitcoin Price Trend')
    if 'ma_7' in df.columns:
        df['ma_7'].plot(label='7-period MA')
        plt.legend()
    plt.ylabel('Price (USD)')
    plt.xlabel('Date')
    plt.grid()
    plt.show()

def plot_volatility(df):
    if 'volatility_7' not in df.columns:
        df = calculate_volatility(df)
    plt.figure(figsize=(12, 6))
    df['volatility_7'].plot(title='Bitcoin Price Volatility (7-day)')
    plt.ylabel('Volatility')
    plt.xlabel('Date')
    plt.grid()
    plt.show()

def generate_report(df):
    df = calculate_moving_average(df)
    df = calculate_volatility(df)
    print("\n=== Bitcoin Price Analysis Report ===")
    print(f"Time Period: {df.index[0]} to {df.index[-1]}")
    print(f"Number of Data Points: {len(df)}")
    print("\nPrice Statistics:")
    print(df['price_usd'].describe())
    print(f"\nLatest Price: ${df['price_usd'].iloc[-1]:,.2f}")
    print(f"24h Change: {df['price_change_24h'].iloc[-1]:.2f}%")
    plot_price_trend(df)
    plot_volatility(df)
    # print(df.head())


# ==============================

