
import requests
import os
from datetime import datetime
from bitcoin_full_pb2 import BitcoinFullData

def fetch_historical_data(days=30):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": str(days)
    }
    response = requests.get(url, params=params)
    
    try:
        data = response.json()
        if "prices" not in data:
            print("❌ Unexpected response from API:")
            print(data)
            raise ValueError("Missing 'prices' field in API response")
        
        print(f"✅ Received {len(data['prices'])} data points")
        return data

    except Exception as e:
        print("❌ Error parsing API response:")
        print(response.text)
        raise e

def save_historical_data_as_protobuf(data, folder="src/data/"):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "bitcoin_historical_hourly.pb")
    with open(filepath, "wb") as f:
        for timestamp_ms, price in data["prices"]:
            msg = BitcoinFullData(
                timestamp=int(timestamp_ms / 1000),
                current_price=price,
                source="CoinGecko"
            )
            serialized = msg.SerializeToString()
            f.write(len(serialized).to_bytes(4, "little") + serialized)
    print(f"📦 Saved historical hourly data to {filepath}")

if __name__ == "__main__":
    try:
        data = fetch_historical_data()
        save_historical_data_as_protobuf(data)
        print("✅ Script complete. Historical data saved.")
    except Exception as e:
        print("❗ Aborting script due to error.")
