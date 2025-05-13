# src/bitcoin_utils.py

import os
import requests
import struct
from datetime import datetime
from bitcoin_full_pb2 import BitcoinFullData

def fetch_btc_data_dict():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin"}
    response = requests.get(url, params=params)
    data = response.json()[0]
    data["timestamp"] = int(datetime.utcnow().timestamp())
    data["source"] = "coingecko"
    return data

def dict_to_protobuf(data_dict):
    return BitcoinFullData(
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

def save_to_length_delimited_file(proto_obj, file_path):
    with open(file_path, "ab") as f:
        msg = proto_obj.SerializeToString()
        size = struct.pack("I", len(msg))
        f.write(size + msg)

def load_length_delimited_protobuf_file(file_path):
    messages = []
    with open(file_path, "rb") as f:
        while True:
            size_bytes = f.read(4)
            if not size_bytes:
                break
            size = struct.unpack("I", size_bytes)[0]
            msg_data = f.read(size)
            msg = BitcoinFullData()
            msg.ParseFromString(msg_data)
            messages.append(msg)
    return messages

def protobufs_to_dataframe(messages):
    import pandas as pd
    rows = []
    for msg in messages:
        rows.append({
            "timestamp": msg.timestamp,
            "id": msg.id,
            "symbol": msg.symbol,
            "name": msg.name,
            "current_price": msg.current_price,
            "market_cap": msg.market_cap,
            "total_volume": msg.total_volume,
            "high_24h": msg.high_24h,
            "low_24h": msg.low_24h,
            "price_change_24h": msg.price_change_24h,
            "market_cap_rank": msg.market_cap_rank,
            "circulating_supply": msg.circulating_supply,
            "ath": msg.ath,
            "atl": msg.atl,
            "source": msg.source,
            "last_updated": msg.last_updated,
        })
    return pd.DataFrame(rows)