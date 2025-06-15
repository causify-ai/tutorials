"""
Customerio.example.py

This script loads simulated Customer.io event data and performs time series analysis using ARIMA,
including forecasting, anomaly detection, and spike visualization.

References:
- ARIMA: https://www.statsmodels.org/
- Pandas: https://pandas.pydata.org/
- Matplotlib: https://matplotlib.org/

Documentation:
- See `Customerio.example.md` for step-by-step explanation of analysis techniques.
"""

from Customerio_utils import retrieve_event_summary, forecast_arima
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd

def detect_spikes_zscore(series: pd.Series, threshold: float = 2.0) -> pd.DataFrame:
    """
    Detect anomalies based on Z-score.

    :param series: Time series to analyze
    :param threshold: Z-score threshold
    :return: DataFrame with anomaly points
    """
    z_scores = (series - series.mean()) / series.std()
    anomalies = z_scores[abs(z_scores) > threshold]
    return anomalies.to_frame(name="z_score")


if __name__ == "__main__":
    # Step 1: Load summarized daily data
    summary_df = retrieve_event_summary()

    # Step 2: Forecast future event trends using ARIMA
    results = forecast_arima(summary_df)

    # Step 3: Evaluate and plot results for each event
    for event, data in results.items():
        y_true = data["y_true"]
        y_pred = data["y_pred"]
        dates = data["dates"]

        # Calculate errors
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        print(f"{event} — MAE: {mae:.2f}, RMSE: {rmse:.2f}")

        # Plot forecast vs actual
        plt.figure(figsize=(10, 4))
        plt.plot(dates, y_true, label="Actual", color="green")
        plt.plot(dates, y_pred, label="Forecast", color="orange", linestyle="--")
        plt.title(f"{event} Forecast vs Actual")
        plt.xlabel("Date")
        plt.ylabel("Event Count")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Step 4: Detect and display anomalies
        full_series = summary_df[event].asfreq("D").fillna(0)
        anomalies_df = detect_spikes_zscore(full_series)

        if not anomalies_df.empty:
            print(f"Anomalies for {event}:")
            for date, row in anomalies_df.iterrows():
                level = "High Spike" if row["z_score"] > 0 else "Sharp Drop"
                print(f"  {date} — z: {row['z_score']:.2f} ({level})")