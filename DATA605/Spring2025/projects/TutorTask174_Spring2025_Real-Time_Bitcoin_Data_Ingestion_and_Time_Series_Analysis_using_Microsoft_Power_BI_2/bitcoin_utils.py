# bitcoin_utils.py

import requests
import pandas as pd
from datetime import datetime
import os

def fetch_bitcoin_price():
    """
    Fetch the current Bitcoin price data from CoinGecko API.
    Returns a dictionary with timestamp, USD price, and market cap.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_last_updated_at': 'true'
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raises exception if API call fails

    data = response.json()
    timestamp = datetime.utcfromtimestamp(data['bitcoin']['last_updated_at']).strftime('%Y-%m-%d %H:%M:%S')

    return {
        'timestamp': timestamp,
        'price_usd': data['bitcoin']['usd'],
        'market_cap_usd': data['bitcoin']['usd_market_cap']
    }

def append_data_to_csv(data, filename='bitcoin_price_data.csv'):
    """
    Append a single row of Bitcoin data to a CSV file. Creates the file if it doesn't exist.
    """
    df = pd.DataFrame([data])
    file_exists = os.path.isfile(filename)
    df.to_csv(filename, mode='a', index=False, header=not file_exists)

def fetch_and_store():
    """
    Helper function to fetch data and save it to CSV.
    """
    try:
        data = fetch_bitcoin_price()
        append_data_to_csv(data)
        print(f"Fetched and saved data: {data}")
    except Exception as e:
        print(f"Error fetching data: {e}")
def transform_bitcoin_data(input_file='bitcoin_price_data.csv', output_file='bitcoin_price_transformed.csv'):
    """
    Transform raw Bitcoin price data:
    - Parse timestamp
    - Calculate percentage change in price
    - Calculate 7-period moving average
    - Calculate 15-period rolling volatility
    - Save transformed data
    """
    try:
        df = pd.read_csv(input_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values(by='timestamp', inplace=True)

        # Percentage change
        df['price_change_pct'] = df['price_usd'].pct_change().fillna(0) * 100

        # 7-period moving average
        df['moving_avg_price'] = df['price_usd'].rolling(window=7).mean()

        # --- add rolling 15-period volatility (std dev) ---
        df['volatility_15m'] = df['price_usd'].rolling(window=15).std()

        # Write out
        df.to_csv(output_file, index=False)
        print(f"Transformed data saved to {output_file}")
    except Exception as e:
        print(f"Error during transformation: {e}")
