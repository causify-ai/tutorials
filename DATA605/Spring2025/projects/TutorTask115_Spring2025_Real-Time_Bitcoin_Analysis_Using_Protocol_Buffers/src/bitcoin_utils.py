# src/bitcoin_utils.py

import os
import requests
from datetime import datetime
from src.bitcoin_full_pb2 import BitcoinFullData

def fetch_btc_data_dict():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": "bitcoin"
    }
    response = requests.get(url, params=params)
    data = response.json()[0]
    data["timestamp"] = int(datetime.utcnow().timestamp())
    data["source"] = "coingecko"
    return data

def save_to_daily_file(data_dict):
    proto_obj = BitcoinFullData(
        timestamp=data_dict["timestamp"],
        id=data_dict.get("id", ""),
        symbol=data_dict.get("symbol", ""),
        name=data_dict.get("name", ""),
        image=data_dict.get("image", ""),
        current_price=data_dict.get("current_price", 0.0),
        market_cap=data_dict.get("market_cap", 0.0),
        market_cap_rank=data_dict.get("market_cap_rank", 0),
        fully_diluted_valuation=data_dict.get("fully_diluted_valuation", 0.0),
        total_volume=data_dict.get("total_volume", 0.0),
        high_24h=data_dict.get("high_24h", 0.0),
        low_24h=data_dict.get("low_24h", 0.0),
        price_change_24h=data_dict.get("price_change_24h", 0.0),
        price_change_percentage_24h=data_dict.get("price_change_percentage_24h", 0.0),
        market_cap_change_24h=data_dict.get("market_cap_change_24h", 0.0),
        market_cap_change_percentage_24h=data_dict.get("market_cap_change_percentage_24h", 0.0),
        circulating_supply=data_dict.get("circulating_supply", 0.0),
        total_supply=data_dict.get("total_supply", 0.0),
        max_supply=data_dict.get("max_supply", 0.0),
        ath=data_dict.get("ath", 0.0),
        ath_change_percentage=data_dict.get("ath_change_percentage", 0.0),
        ath_date=data_dict.get("ath_date", ""),
        atl=data_dict.get("atl", 0.0),
        atl_change_percentage=data_dict.get("atl_change_percentage", 0.0),
        atl_date=data_dict.get("atl_date", ""),
        last_updated=data_dict.get("last_updated", ""),
        source=data_dict.get("source", "")
    )

    # Always write to src/data/ even when running from another directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(script_dir, "data")
    os.makedirs(folder, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    path = os.path.join(folder, f"bitcoin_data_{date_str}.pb")

    with open(path, "ab") as f:
        f.write(proto_obj.SerializeToString())