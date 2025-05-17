import matplotlib.pyplot as plt
import os
import pandas as pd

# Load data
price_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bitcoin_prices.json')
df = pd.read_json(price_path, lines=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['pct_change'] = df['price'].pct_change() * 100

# Detect anomalies
anomalies = df[abs(df['pct_change']) > 2]

# Plot
plt.figure(figsize=(12,6))
plt.plot(df['timestamp'], df['price'], label='BTC Price')
plt.scatter(anomalies['timestamp'], anomalies['price'], color='red', label='Anomaly (>±5%)')
plt.xlabel('Time')
plt.ylabel('Price (USD)')
plt.title('Bitcoin Price with Anomalies')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("../results/bitcoin_price_anomalies_plot.png")
plt.show()

print("\nSaved visualization to results/bitcoin_price_anomalies_plot.png")
