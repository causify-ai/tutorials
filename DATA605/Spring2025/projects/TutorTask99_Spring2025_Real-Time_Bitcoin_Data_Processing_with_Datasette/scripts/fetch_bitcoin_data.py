import requests
import pandas as pd
from datetime import datetime

def fetch_bitcoin_prices():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "365",   # last 1 year
        "interval": "daily"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise error if the API fails

    data = response.json()

    # Extract prices
    prices = data.get('prices', [])
    if not prices:
        print("No price data found.")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

if __name__ == "__main__":
    df = fetch_bitcoin_prices()
    if df is not None:
        filename = f"/Users/riyayrd/bitcoin_datasette/data/bitcoin_prices_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save.")
