"""
bitcoin.example.py

Demonstrates real-time Bitcoin data ingestion, validation, and advanced time series analysis
using the BitcoinAPI pipeline. Includes validation workflow, data documentation,
trend visualization, volatility detection, and forecasting-ready structure.
"""

import time
import importlib.util
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Dynamically load bitcoin.API.py
spec = importlib.util.spec_from_file_location("bitcoin_api", "./bitcoin.API.py")
module = importlib.util.module_from_spec(spec)
sys.modules["bitcoin_api"] = module
spec.loader.exec_module(module)

# Import the BitcoinAPI class
BitcoinAPI = module.BitcoinAPI


class BitcoinMonitor:
    """
    Class that monitors Bitcoin data periodically, performs validation using Great Expectations,
    and provides time series analysis and forecasting capabilities.
    """

    def __init__(self, interval_seconds: int = 3, run_count: int = 5, log_file: str = "bitcoin_price_log.csv"):
        """
        Initialize the monitor with configuration parameters.

        :param interval_seconds: Number of seconds between each data fetch.
        :param run_count: Number of fetch-and-validate iterations to perform.
        :param log_file: Path to the CSV log file for data storage.
        """
        self.api = BitcoinAPI(log_file=log_file)
        self.interval = interval_seconds
        self.run_count = run_count
        self.log_file = log_file

    def run_loop(self, verbose: bool = False):
        """
        Run the data ingestion loop, validating data in each iteration.
        Also logs failure records to logs/validation_fail_log.txt.

        :param verbose: If True, print detailed validation and fetch logs.
        """
        os.makedirs("logs", exist_ok=True)
        log_path = "logs/validation_fail_log.txt"

        # If file does not exist, write intro message
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                f.write("This is a log record to track alerts for expectation failures and provide early warnings for potential data issues.\n\n")

        for i in range(self.run_count):
            print(f"\n[INFO] Run {i + 1} of {self.run_count}")
            result = self.api.run(verbose=verbose)

            # Skip if fetch failed or incomplete
            if result.get("skipped", False):
                print("[INFO] Skipped due to empty or failed fetch.")
                continue

            if not result["success"]:
                print("[WARNING] Validation failed.")

                # Write to log file
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                passed = result["statistics"]["successful_expectations"]
                total = result["statistics"]["evaluated_expectations"]
                message = f"[{now}] Validation FAILED ({passed} / {total})\n"
                with open(log_path, "a") as f:
                    f.write(message)

            else:
                print("[INFO] Validation passed.")

            time.sleep(self.interval)

    def analyze_trend(self) -> pd.DataFrame:
        """
        Analyze Bitcoin price trends, detect volatility spikes, and save a visualization plot.

        :return: A processed DataFrame containing trend and volatility metrics.
        """
        os.makedirs("./images", exist_ok=True)

        df = pd.read_csv(self.log_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df["formatted_time"] = df["timestamp"].dt.strftime("%H:%M:%S")
        df["price_ma"] = df["price_usd"].rolling(window=3).mean()
        df["price_diff"] = df["price_usd"].diff()
        df["price_volatility"] = df["price_usd"].rolling(window=3).std()

        z_score = (df["price_volatility"] - df["price_volatility"].mean()) / df["price_volatility"].std()
        df["volatility_spike"] = z_score.abs() > 2

        # Plot: Trend and Volatility
        plt.figure(figsize=(12, 6))
        plt.plot(df["formatted_time"], df["price_usd"], marker='o', label="Price (USD)")
        plt.plot(df["formatted_time"], df["price_ma"], linestyle='--', label="3-pt Moving Average")
        plt.fill_between(
            df["formatted_time"],
            (df["price_usd"] - df["price_volatility"]).fillna(method='bfill'),
            (df["price_usd"] + df["price_volatility"]).fillna(method='bfill'),
            color='gray', alpha=0.2, label="Volatility Range"
        )
        step = max(1, len(df) // 15)
        xticks_idx = np.arange(0, len(df), step)
        plt.xticks(xticks_idx, df["formatted_time"].iloc[xticks_idx], rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Bitcoin Price (USD)")
        plt.title("Bitcoin Price Trend with Moving Average and Volatility")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        trend_path = "./images/bitcoin_trend.jpg"
        plt.savefig(trend_path)
        plt.show()
        print(f"[INFO] Plot saved to: {trend_path}")

        # Summary statistics
        print("\nSummary:")
        print(f"Average price: {df['price_usd'].mean():.2f} USD")
        print(f"Max price: {df['price_usd'].max():.2f} USD")
        print(f"Min price: {df['price_usd'].min():.2f} USD")

        # Volatility alert
        spikes = df[df["volatility_spike"]]
        if not spikes.empty:
            print("\n[ALERT] Detected sudden volatility changes at:")
            print(spikes[["timestamp", "price_usd", "price_volatility"]])
        else:
            print("\nNo significant volatility spikes detected.")

        return df

    def generate_forecast(self, df: pd.DataFrame):
        """
        Forecast Bitcoin prices using Holt-Winters Exponential Smoothing.

        :param df: A DataFrame containing historical Bitcoin price data with timestamp.
        """
        df_ts = df.set_index("timestamp")
        if len(df_ts.index) > 1:
            time_delta = df_ts.index[-1] - df_ts.index[-2]
        else:
            time_delta = pd.Timedelta(seconds=3)

        model = ExponentialSmoothing(df_ts["price_usd"], trend="add", seasonal=None)
        fit = model.fit()
        forecast_steps = 100
        forecast_values = fit.forecast(forecast_steps)

        last_time = df_ts.index[-1]
        forecast_index = pd.date_range(start=last_time + time_delta, periods=forecast_steps, freq=time_delta)
        forecast_series = pd.Series(forecast_values.values, index=forecast_index)

        # Plot forecast
        plt.figure(figsize=(12, 6))
        plt.plot(df_ts.index, df_ts["price_usd"], label="Historical Price")
        plt.plot(forecast_series.index, forecast_series.values, linestyle="--", color="orange", label="Forecast (next 100)")
        plt.xlabel("Time")
        plt.ylabel("Bitcoin Price (USD)")
        plt.title("Bitcoin Price Forecast (Holt-Winters)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        forecast_path = "./images/bitcoin_forecast.jpg"
        plt.savefig(forecast_path)
        plt.show()
        print(f"[INFO] Forecast plot saved to: {forecast_path}")


if __name__ == "__main__":
    monitor = BitcoinMonitor(interval_seconds=3, run_count=5)
    monitor.run_loop(verbose=False)
    df = monitor.analyze_trend()
    monitor.generate_forecast(df)
