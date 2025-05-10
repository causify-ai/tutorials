import requests
import pandas as pd

def fetch_bitcoin_data(api_key: str, days: int = 365, interval: str = 'daily') -> pd.DataFrame:
    headers = {
        'x-cg-demo-api-key': api_key
    }

    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': str(days),
        'interval': interval
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
