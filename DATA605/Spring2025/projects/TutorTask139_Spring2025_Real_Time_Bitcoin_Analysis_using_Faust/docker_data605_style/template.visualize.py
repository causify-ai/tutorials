import pandas as pd
import matplotlib.pyplot as plt
import json

# Load data from file
def load_data(file_path='btc_prices.json'):
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

# Plot price and rolling average
def plot_prices(df, window=5):
    df['rolling_avg'] = df['price'].rolling(window=window).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['price'], label='Price')
    plt.plot(df.index, df['rolling_avg'], label=f'Rolling Avg ({window})', linestyle='--')
    plt.title('Bitcoin Price with Rolling Average')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Entry point
if __name__ == "__main__":
    df = load_data()
    plot_prices(df)
