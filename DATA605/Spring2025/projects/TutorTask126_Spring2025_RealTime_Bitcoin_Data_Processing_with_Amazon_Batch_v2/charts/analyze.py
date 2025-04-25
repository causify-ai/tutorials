import pandas as pd
import matplotlib.pyplot as plt 

#load csv file
df = pd.read_csv("btc_prices_data.csv")

#convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

#sort by time
df = df.sort_values('timestamp')

#plot BTC price
plt.figure(figsize=(10,5))
plt.plot(df['timestamp'],df['price_usd'], label='BTC price')

#Add a 5-point moving average
df['moving_avg'] = df['price_usd'].rolling(window=5).mean()
plt.plot(df['timestamp'], df['moving_avg'], label='5-point Moving Avg', linestyle='--')

#Customize plot
plt.xlabel("Time")
plt.ylabel("Price (USD)")
plt.title("Bitcoin Price Trend")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)

plot_file = "btc_price_plot.png"
plt.savefig(plot_file)
print(f"Plot saved as {plot_file}")

plt.show()