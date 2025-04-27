import pandas as pd
import requests

def load_historical_data(filepath):
    df = pd.read_csv(filepath)
    df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
    df = df[['datetime', 'Close']].dropna()
    df.rename(columns={'datetime': 'ds', 'Close': 'y'}, inplace=True)
    df = df.set_index('ds').resample('D').agg({'y': 'last'}).reset_index()
    return df

def fetch_live_data(days=365, currency='usd'):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        'vs_currency': currency,
        'days': days,
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'y'])
    df['ds'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['ds', 'y']]

def merge_and_clean_data(historical_df, live_df):
    final_df = pd.concat([historical_df, live_df])
    final_df.drop_duplicates(subset='ds', keep='last', inplace=True)
    final_df = final_df.set_index('ds').resample('D').agg({'y': 'last'}).reset_index()
    return final_df
