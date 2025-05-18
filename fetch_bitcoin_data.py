import requests
import pandas as pd
from datetime import datetime

def fetch_bitcoin_data(days=365):
    '''
    Fetch historical Bitcoin price data from CoinGecko API for the past `days`.

    Parameters:
        days (int): Number of past days to fetch data for.

    Returns:
        pd.DataFrame: DataFrame containing 'Timestamp' and 'Price' columns.
    '''
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        prices = data['prices']
        df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

        print(f"✅ Successfully fetched {len(df)} records (not saved to file)")
        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()
