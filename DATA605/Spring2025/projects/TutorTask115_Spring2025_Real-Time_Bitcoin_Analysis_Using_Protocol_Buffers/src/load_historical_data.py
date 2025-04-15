import requests
import os
from datetime import datetime
import bitcoin_full_pb2

def fetch_historical_data(days=30):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}

    response = requests.get(url, params=params)

    try:
        data = response.json()
        if "prices" not in data:
            print("❌ Unexpected response from API:", data)
            raise ValueError("Missing 'prices' field in API response")
        
        print(f"✅ Received {len(data['prices'])} data points")
        return data

    except Exception as e:
        print("❌ Error parsing API response:", response.text)
        raise e

def save_historical_data_as_protobuf(data):
    os.makedirs("data", exist_ok=True)
    file_path = "data/bitcoin_historical_hourly.pb"

    with open(file_path, "wb") as f:
        for i in range(len(data["prices"])):
            timestamp_ms, price = data["prices"][i]
            _, volume = data["total_volumes"][i]
            _, market_cap = data["market_caps"][i]

            msg = bitcoin_full_pb2.BitcoinFullData()
            msg.timestamp = int(timestamp_ms / 1000)
            msg.current_price = price
            msg.total_volume = volume
            msg.market_cap = market_cap
            msg.source = "CoinGecko_Historical"
            msg.id = "bitcoin"
            msg.symbol = "btc"
            msg.name = "Bitcoin"
            msg.last_updated = datetime.utcfromtimestamp(timestamp_ms / 1000).isoformat()

            serialized = msg.SerializeToString()
            f.write(len(serialized).to_bytes(4, byteorder="little"))
            f.write(serialized)

    print(f"📦 Saved historical hourly data to {file_path}")

if __name__ == "__main__":
    try:
        data = fetch_historical_data()
        save_historical_data_as_protobuf(data)
        print("✅ Script complete. Historical data saved.")
    except Exception as e:
        print("❗ Aborting script due to error.")