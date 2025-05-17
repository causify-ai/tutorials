import os

import requests
import pandas as pd
import time

def fetch_btc_data(days=120):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        #"interval": "hourly"
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    prices = data["prices"]
    volumes = data["total_volumes"]

    records = []
    for i in range(len(prices)):
        ts = prices[i][0]
        price = prices[i][1]
        volume = volumes[i][1]
        records.append({
            "timestamp": pd.to_datetime(ts, unit="ms"),
            "price": price,
            "volume": volume
        })

    # Full output path
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "btc_price_history.csv"))
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print("Saved data to btc_price_history.csv")

if __name__ == "__main__":
    fetch_btc_data(days=365)
