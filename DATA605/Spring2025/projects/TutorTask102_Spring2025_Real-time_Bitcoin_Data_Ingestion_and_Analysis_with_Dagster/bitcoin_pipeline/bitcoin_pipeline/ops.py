import requests
import pandas as pd
from dagster import op
from datetime import datetime

@op
def fetch_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    timestamp = datetime.utcnow().isoformat()
    return {"timestamp": timestamp, "price": data["bitcoin"]["usd"]}

@op
def process_data(raw_data: dict) -> pd.DataFrame:
    df = pd.DataFrame([raw_data])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

@op
def save_to_csv(df: pd.DataFrame):
    filename = "bitcoin_prices.csv"
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv(filename, index=False)