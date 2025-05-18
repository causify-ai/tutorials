import pandas as pd
import cloudpickle
import os
import logging
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from ipywidgets import widgets
from IPython.display import display, clear_output

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
# Utility Function 3: Fetch Bitcoin Data
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
# Utility Function 4: Combined Interactive Dashboard with Plot
# -----------------------------------------------------------------------------
def interactive_dashboard(ma_window=5, threshold=2.0):
    """
    Creates an interactive dashboard with sliders to control the moving average window 
    and anomaly detection threshold, and updates the plot dynamically.
    """
    # Clear previous output
    clear_output(wait=True)
    
    serialize_analysis_functions()
    ma_func, anomaly_func = load_analysis_functions()

    # Fetch Bitcoin data
    df = fetch_bitcoin_data()
    if df is None:
        print("⚠️ Failed to fetch data.")
        return

    # Calculate Moving Average and Anomalies
    ma = ma_func(df['price'], window=ma_window)
    anomalies = anomaly_func(df['price'], threshold=threshold)

    # --- Show Summary Stats ---
    print(f"📊 Stats (Last 24h):")
    print(f"• Latest Price: ${df['price'].iloc[-1]:,.2f}")
    print(f"• Mean Price:   ${df['price'].mean():,.2f}")
    print(f"• Std Dev:      ${df['price'].std():,.2f}")
    print(f"• Anomalies Detected: {len(anomalies)}")
    print()

    # --- Plot the Dashboard ---
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

    # --- Interactive Widgets ---
    # Create sliders for MA window and anomaly threshold
    ma_slider = widgets.IntSlider(value=ma_window, min=2, max=20, step=1, description='MA Window')
    threshold_slider = widgets.FloatSlider(value=threshold, min=0.5, max=4.0, step=0.1, description='Anomaly Threshold')
    refresh_button = widgets.Button(description="🔄 Refresh")

    # Output area for updating the plot
    out = widgets.Output()

    def on_refresh_clicked(b):
        with out:
            interactive_dashboard(ma_slider.value, threshold_slider.value)

    refresh_button.on_click(on_refresh_clicked)

    # Display widgets and output area
    ui = widgets.VBox([ma_slider, threshold_slider, refresh_button])
    display(ui, out)