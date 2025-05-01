import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_market_chart(interval: str, days: int):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data['prices']

def process_price_data(raw_data):
    df = pd.DataFrame(raw_data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.sort_values("timestamp")
    return df

def main():
    print("Fetching minutely data (last 7 days)...")
    last_7_days = fetch_market_chart("minutely", 7)
    df_minutely = process_price_data(last_7_days)

    print("Fetching hourly data (last 30 days)...")
    last_30_days = fetch_market_chart("hourly", 30)
    df_hourly = process_price_data(last_30_days)

    # Filter hourly to only 8 to 30 days ago
    cutoff = datetime.now() - timedelta(days=7)
    df_hourly = df_hourly[df_hourly["timestamp"] < cutoff]

    # Combine datasets
    full_df = pd.concat([df_hourly, df_minutely]).reset_index(drop=True)
    full_df = full_df.drop_duplicates(subset="timestamp").sort_values("timestamp")

    print(f"Fetched {len(full_df)} records.")
    full_df.to_csv("bitcoin_prices.csv", index=False)
    print("Saved to bitcoin_prices.csv")

if __name__ == "__main__":
    main()

