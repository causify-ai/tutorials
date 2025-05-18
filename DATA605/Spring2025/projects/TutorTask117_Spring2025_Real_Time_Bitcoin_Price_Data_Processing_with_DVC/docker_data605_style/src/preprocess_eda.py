import os
import pandas as pd
import matplotlib.pyplot as plt

def preprocess(filepath="data/bitcoin_prices.csv", outpath="data/cleaned_bitcoin.csv"):
    """
    Load BTC price data, compute diff and rolling average, save cleaned CSV.
    Handles mixed timestamp formats using pandas auto-parsing.
    """
    df = pd.read_csv(filepath)

    # ✅ Fix timestamp parsing issue by using auto-detection and fallback for bad values
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    df = df.sort_values(by='timestamp')
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

    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['price'], label='Price (USD)', linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Bitcoin Price')
    plt.title('Bitcoin Price Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"✅ Plot saved to {output_path}")
