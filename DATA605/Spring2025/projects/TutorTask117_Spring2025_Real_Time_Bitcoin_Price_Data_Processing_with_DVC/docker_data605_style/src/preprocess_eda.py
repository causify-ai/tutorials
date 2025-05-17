# src/preprocess_eda.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def preprocess(filepath="data/bitcoin_prices.csv", outpath="data/cleaned_bitcoin.csv"):
    """
    Load BTC price data, compute diff and rolling average, save cleaned CSV.
    """
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['price_diff'] = df['price'].diff()
    df['rolling_avg'] = df['price'].rolling(window=5).mean()

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    df.to_csv(outpath, index=False)
    return df

def plot_data(df, output_path="Output/bitcoin_price_plot.png"):
    """
    Save a time series line chart from the cleaned data.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.plot(x='timestamp', y='price', title="Bitcoin Price Over Time", figsize=(10, 5))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
