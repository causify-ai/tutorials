import requests
import pandas as pd
from datetime import datetime, timezone
import os

#local file to save btc_prices
CSV_FILE = "btc_prices_data.csv"

#fetch current bitcoin price from CoinGecko
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids":"bitcoin", "vs_currencies":"usd"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        price = response.json()["bitcoin"]["usd"]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return timestamp, price
    except requests.RequestException as e:
        print("Error fetching BTC price:",e)
        return None, None

#save timestamp and price to a csv file
def save_to_csv(timestamp, price):
    data = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price_usd"])

    if os.path.exists(CSV_FILE):
        data.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        data.to_csv(CSV_FILE,index=False)
    
    print(f"Saved: {timestamp} | ${price}")

if __name__ == "__main__":
    ts, price = get_btc_price()
    if ts and price:
        save_to_csv(ts, price)
