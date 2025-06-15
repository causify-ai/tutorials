# forecast_with_prophet.py

import os
import pandas as pd
from prophet import Prophet

def run_forecast():
    # Load input
    ewma_path = "../report/ewma_anomalies.csv"
    if not os.path.exists(ewma_path):
        print("[ERROR] EWMA file not found.")
        return

    ewma_df = pd.read_csv(ewma_path, parse_dates=["window_start"])

    # Prepare data
    df_prophet = ewma_df.rename(columns={
        "window_start": "ds",
        "tx_count_1min": "y"
    })[["ds", "y"]].dropna()

    # Fit model
    model = Prophet(interval_width=0.95, daily_seasonality=False)
    model.fit(df_prophet)

    # Forecast next 30 minutes
    future = model.make_future_dataframe(periods=30, freq="min")
    forecast = model.predict(future)

    # Save output
    os.makedirs("../report", exist_ok=True)
    forecast.to_csv("../report/prophet_forecast.csv", index=False)
    print("[INFO] Forecast saved to ../report/prophet_forecast.csv")

if __name__ == "__main__":
    run_forecast()