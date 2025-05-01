import pandas as pd
import cloudpickle
import os
import logging
from sklearn.model_selection import train_test_split
from datetime import datetime

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Utility Function 1: Serialize Analysis Functions
# -----------------------------------------------------------------------------
def serialize_analysis_functions():
    """
    Serializes the analysis functions (moving average and anomaly detection)
    to disk to avoid recomputing them.
    """
    if not os.path.exists("ma_func.pkl"):
        ma_func = lambda data, window=5: data.rolling(window=window).mean()
        anomaly_func = lambda data, threshold=2.0: data[(data - data.mean()).abs() > threshold * data.std()]
        with open("ma_func.pkl", "wb") as f:
            cloudpickle.dump(ma_func, f)
        with open("anomaly_func.pkl", "wb") as f:
            cloudpickle.dump(anomaly_func, f)

# -----------------------------------------------------------------------------
# Utility Function 2: Load Analysis Functions
# -----------------------------------------------------------------------------
def load_analysis_functions():
    """
    Loads the serialized analysis functions (moving average and anomaly detection)
    from disk.
    """
    with open("ma_func.pkl", "rb") as f:
        ma_func = cloudpickle.load(f)
    with open("anomaly_func.pkl", "rb") as f:
        anomaly_func = cloudpickle.load(f)
    return ma_func, anomaly_func

# -----------------------------------------------------------------------------
# Utility Function 3: Split Data (for general usage)
# -----------------------------------------------------------------------------
def split_data(df: pd.DataFrame, target_column: str, test_size: float = 0.2):
    """
    Splits the dataset into training and testing sets.

    :param df: full dataset
    :param target_column: name of the target column
    :param test_size: proportion of test data (default = 0.2)
    
    :return: X_train, X_test, y_train, y_test
    """
    logger.info("Splitting data into train and test sets")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=42)

# -----------------------------------------------------------------------------
# Utility Function 4: Fetch Bitcoin Data
# -----------------------------------------------------------------------------
def fetch_bitcoin_data():
    """
    Fetches Bitcoin price data from the CoinGecko API for the last 24 hours.
    Returns the data as a Pandas DataFrame.
    """
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {'vs_currency': 'usd', 'days': '1'}
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, params=params, headers=headers)

    if res.status_code != 200:
        print(f"❌ Error: Status code {res.status_code}")
        return None

    data = res.json()
    if 'prices' not in data:
        print("❌ 'prices' key missing in response")
        return None

    df = pd.DataFrame(data['prices'], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

# -----------------------------------------------------------------------------
# Utility Function 5: Plot Dashboard
# -----------------------------------------------------------------------------
def plot_dashboard(df, ma, anomalies, ma_window, threshold):
    """
    Plots the Bitcoin price data along with the moving average and anomalies.

    :param df: DataFrame containing the Bitcoin price data
    :param ma: Moving average series
    :param anomalies: Anomalies detected in the price data
    :param ma_window: Moving average window size
    :param threshold: Threshold for anomaly detection
    """
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['price'], label="BTC Price", color='skyblue')
    plt.plot(ma.index, ma, label=f"MA (window={ma_window})", color='orange')
    plt.scatter(anomalies.index, anomalies, color='red', label="Anomalies", zorder=5)
    plt.title(f"BTC/USD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
