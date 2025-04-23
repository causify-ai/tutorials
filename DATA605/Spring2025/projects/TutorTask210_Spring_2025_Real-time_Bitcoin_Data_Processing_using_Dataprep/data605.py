from dataprep.connector import Connector
import pandas as pd
import requests
import time

# Create a function to fetch real-time Bitcoin price using CoinGecko API
def fetch_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        price = data['bitcoin']['usd']
        timestamp = pd.Timestamp.now()
        return {'timestamp': timestamp, 'price_usd': price}
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Initialize an empty list to collect data over time
collected_data = []

collection_duration_seconds = 10800  # 3 hour
interval_seconds = 10 

iterations = collection_duration_seconds // interval_seconds

print(f"Starting data collection for {collection_duration_seconds/60} minutes...")

for i in range(iterations):
    data_point = fetch_bitcoin_data()
    if data_point:
        collected_data.append(data_point)
        print(f"[{data_point['timestamp']}] Price: ${data_point['price_usd']}")
    time.sleep(interval_seconds)

# Save to CSV
bitcoin_df = pd.DataFrame(collected_data)
bitcoin_df.to_csv('bitcoin_real_time_data2.csv', index=False)

print("Data collection completed and saved to 'bitcoin_real_time_data2.csv'.")

