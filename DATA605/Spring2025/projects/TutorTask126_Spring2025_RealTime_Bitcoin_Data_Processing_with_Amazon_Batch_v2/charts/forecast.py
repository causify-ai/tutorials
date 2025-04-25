import pandas as pd 
import matplotlib.pyplot as plt 
from statsmodels.tsa.arima.model import ARIMA 
from datetime import timedelta

#load and prepare data
df = pd.read_csv("btc_prices_data.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

#set timestamp as index
df.set_index('timestamp', inplace=True)

#create and fit ARIMA model
model = ARIMA(df['price_usd'], order=(3,1,2)) #you can tune (p,d,q)
fitted_model = model.fit()

#forecast next 5 points
forecast_steps = 5
forecast = fitted_model.forecast(steps=forecast_steps)

#generate future timestamps
last_timestamp = df.index[-1]
future_timestamps = [last_timestamp + timedelta(minutes=5 * (i + 1)) for i in range(forecast_steps)]

#plot actual and forecasted prices
plt.figure(figsize=(10, 5))
plt.plot(df.index, df['price_usd'], label='Actual BTC Price')
plt.plot(future_timestamps, forecast, label='Forecast', linestyle='--', marker='o')

plt.xlabel("Time")
plt.ylabel("Price (USD)")
plt.title("Bitcoin Price Forecast")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.grid(True)

#save and show plot
plot_file = "btc_forecast_plot.png"
plt.savefig(plot_file)
plt.show()
print(f"Forecast plot saved as {plot_file}")
