import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from bitcoin_utils import fetch_bitcoin_data

# Fetch and prepare data
df = fetch_bitcoin_data(api_key="CG-5pibUvyXCBs3EpUFkQg3nDoX", days=365)
df["date"] = pd.to_datetime(df["date"])
df.set_index("date", inplace=True)

# Simple moving average
df["MA30"] = df["price"].rolling(window=30).mean()

# Plot price and MA
plt.figure(figsize=(10,5))
plt.plot(df.index, df["price"], label="Price")
plt.plot(df.index, df["MA30"], label="30-Day MA")
plt.legend()
plt.title("Bitcoin Price and 30-Day Moving Average")
plt.savefig("bitcoin_forecast_plot.png")
plt.close()

# ARIMA Forecasting
model = ARIMA(df["price"], order=(5,1,0))
model_fit = model.fit()
forecast = model_fit.forecast(steps=30)
forecast_index = pd.date_range(start=df.index[-1], periods=30, freq="D")
forecast_df = pd.DataFrame({"date": forecast_index, "forecast": forecast})
forecast_df.to_csv("bitcoin_prices_with_forecast.csv", index=False)

# Anomaly detection (rolling z-score)
df["rolling_mean"] = df["price"].rolling(window=30).mean()
df["rolling_std"] = df["price"].rolling(window=30).std()
df["z_score"] = (df["price"] - df["rolling_mean"]) / df["rolling_std"]
df["anomaly"] = abs(df["z_score"]) > 2
df.to_csv("bitcoin_prices_with_anomalies.csv")

print("Analysis and plots completed.")
