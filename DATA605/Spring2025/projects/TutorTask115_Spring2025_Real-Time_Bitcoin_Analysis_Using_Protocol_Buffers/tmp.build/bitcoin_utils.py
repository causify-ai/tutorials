
import requests
import time
import os
from datetime import datetime
from bitcoin_full_pb2 import BitcoinFullData
import pandas as pd

# 1.Fetch Real-Time Data from API

def fetch_btc_data_dict():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin"}
    response = requests.get(url, params=params)
    btc = response.json()[0]

    return {
        "timestamp": int(time.time()),
        "id": btc["id"],
        "symbol": btc["symbol"],
        "name": btc["name"],
        "image": btc["image"],
        "current_price": btc["current_price"],
        "market_cap": btc["market_cap"],
        "market_cap_rank": btc["market_cap_rank"],
        "fully_diluted_valuation": btc.get("fully_diluted_valuation", 0.0),
        "total_volume": btc["total_volume"],
        "high_24h": btc["high_24h"],
        "low_24h": btc["low_24h"],
        "price_change_24h": btc["price_change_24h"],
        "price_change_percentage_24h": btc["price_change_percentage_24h"],
        "market_cap_change_24h": btc["market_cap_change_24h"],
        "market_cap_change_percentage_24h": btc["market_cap_change_percentage_24h"],
        "circulating_supply": btc["circulating_supply"],
        "total_supply": btc.get("total_supply", 0.0),
        "max_supply": btc.get("max_supply", 0.0),
        "ath": btc["ath"],
        "ath_change_percentage": btc["ath_change_percentage"],
        "ath_date": btc["ath_date"],
        "atl": btc["atl"],
        "atl_change_percentage": btc["atl_change_percentage"],
        "atl_date": btc["atl_date"],
        "last_updated": btc["last_updated"],
        "source": "CoinGecko"
    }


#  2. Save Record to Daily .pb File

def save_to_daily_file(data_dict, folder="src/data/"):
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"bitcoin_data_{today}.pb")
    msg = BitcoinFullData(**data_dict)
    serialized = msg.SerializeToString()
    with open(filename, "ab") as f:
        f.write(len(serialized).to_bytes(4, "little") + serialized)


# 3. Fetch Historical Hourly Data

def fetch_historical_data(days=30):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    response = requests.get(url, params=params)
    return response.json()


# 💾 4. Save Historical Data as Protobuf
def save_historical_data_as_protobuf(data, folder="src/data/"):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, "bitcoin_historical_hourly.pb")
    with open(filename, "wb") as f:
        for point in data["prices"]:
            timestamp_ms, price = point
            msg = BitcoinFullData(
                timestamp=int(timestamp_ms / 1000),
                current_price=price,
                source="CoinGecko"
            )
            serialized = msg.SerializeToString()
            f.write(len(serialized).to_bytes(4, "little") + serialized)


# 📥 5. Load Protobuf Data From File

def load_protobuf_file(filepath):
    messages = []
    with open(filepath, "rb") as f:
        while True:
            len_bytes = f.read(4)
            if not len_bytes:
                break
            msg_len = int.from_bytes(len_bytes, "little")
            msg_data = f.read(msg_len)
            msg = BitcoinFullData()
            msg.ParseFromString(msg_data)
            messages.append(msg)
    return messages


# 🔁 6. Convert Messages to DataFrame

def protobufs_to_dataframe(messages):
    rows = []
    for m in messages:
        row = {
            "timestamp": datetime.fromtimestamp(m.timestamp),
            "price": m.current_price,
            "volume": m.total_volume,
            "market_cap": m.market_cap,
            "source": m.source
        }
        rows.append(row)
    return pd.DataFrame(rows)
