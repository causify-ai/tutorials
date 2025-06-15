import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller

def plot_rolling_stats(series, window=24, title="Rolling Statistics"):
    """
    Plot rolling mean and standard deviation to visualize stationarity.
    
    Args:
        series (pd.Series): Time series data (e.g., price)
        window (int): Rolling window size
        title (str): Plot title
    """
    roll_mean = series.rolling(window).mean()
    roll_std = series.rolling(window).std()

    plt.figure(figsize=(12, 4))
    plt.plot(series, label="Original", alpha=0.5)
    plt.plot(roll_mean, label=f"Rolling Mean ({window})")
    plt.plot(roll_std, label=f"Rolling Std ({window})")
    plt.title(title)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def run_adf_test(series):
    """
    Run Augmented Dickey-Fuller test for stationarity.
    
    Args:
        series (pd.Series): Time series data
    """
    result = adfuller(series.dropna())
    print("ADF Statistic:", result[0])
    print("p-value:", result[1])
    for key, value in result[4].items():
        print(f"Critical Value ({key}): {value}")
    
    if result[1] < 0.05:
        print("Result: Series is likely stationary (reject H0)")
    else:
        print("Result: Series is likely non-stationary (fail to reject H0)")
