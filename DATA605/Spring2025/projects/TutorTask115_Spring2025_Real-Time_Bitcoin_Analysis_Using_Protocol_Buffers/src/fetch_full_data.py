# Fetches live BTC data from CoinGecko
import requests
import time

def fetch_btc_data_dict():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin"}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if not data:
            print("⚠️ Empty response")
            return None

        btc = data[0]
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
    except Exception as e:
        print("❌ Fetch error:", e)
        return None