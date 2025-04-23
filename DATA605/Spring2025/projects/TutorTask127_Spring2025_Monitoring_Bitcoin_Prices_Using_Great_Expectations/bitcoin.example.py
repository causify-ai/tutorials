"""
bitcoin.example.py

Demonstrates real-time Bitcoin data ingestion, validation, and extended time series analysis
using the BitcoinAPI pipeline. Includes validation workflow, data documentation, and
trend/volatility insights.
"""

import time
import importlib.util
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Dynamically load bitcoin.API.py
spec = importlib.util.spec_from_file_location("bitcoin_api", "./bitcoin.API.py")
module = importlib.util.module_from_spec(spec)
sys.modules["bitcoin_api"] = module
spec.loader.exec_module(module)

# Import the BitcoinAPI class
BitcoinAPI = module.BitcoinAPI


class BitcoinMonitor:
    """
    Monitor Bitcoin data periodically, validate it using Great Expectations,
    and perform extended time series analysis.
    """

    def __init__(self, interval_seconds: int = 3, run_count: int = 5, log_file: str = "bitcoin_price_log.csv"):
        """
        Initialize the monitor.

        :param interval_seconds: Number of seconds between each data fetch.
        :param run_count: Number of iterations to fetch and validate.
        :param log_file: Path to the CSV log file.
        """
        self.api = BitcoinAPI(log_file=log_file)
        self.interval = interval_seconds
        self.run_count = run_count
        self.log_file = log_file

    def run_loop(self):
        """
        Run the monitoring loop: fetch, validate, log, and summarize.
        """
        for i in range(self.run_count):
            print(f"\n[INFO] Run {i + 1} of {self.run_count}")
            result = self.api.run()

            if not result["success"]:
                print("[WARNING] Validation failed in this run.")

            time.sleep(self.interval)

    def analyze_trend(self):
        """
        Perform extended time series analysis on Bitcoin price data.
        """
        df = pd.read_csv(self.log_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df["formatted_time"] = df["timestamp"].dt.strftime("%H:%M:%S")

        # Compute additional metrics
        df["price_ma"] = df["price_usd"].rolling(window=3).mean()
        df["price_diff"] = df["price_usd"].diff()
        df["price_volatility"] = df["price_usd"].rolling(window=3).std()

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.plot(df["formatted_time"], df["price_usd"], marker='o', label="Price (USD)")
        plt.plot(df["formatted_time"], df["price_ma"], linestyle='--', label="3-pt Moving Average")
        plt.fill_between(df["formatted_time"], 
                         (df["price_usd"] - df["price_volatility"]).fillna(method='bfill'),
                         (df["price_usd"] + df["price_volatility"]).fillna(method='bfill'),
                         color='gray', alpha=0.2, label="Volatility Range")

        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Bitcoin Price (USD)")
        plt.title("Bitcoin Price Trend with Moving Average and Volatility")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Summary
        print("\nSummary:")
        print(f"Average price: {df['price_usd'].mean():.2f} USD")
        print(f"Max price: {df['price_usd'].max():.2f} USD")
        print(f"Min price: {df['price_usd'].min():.2f} USD")


if __name__ == "__main__":
    monitor = BitcoinMonitor(interval_seconds=3, run_count=5)
    monitor.run_loop()
    monitor.analyze_trend()
