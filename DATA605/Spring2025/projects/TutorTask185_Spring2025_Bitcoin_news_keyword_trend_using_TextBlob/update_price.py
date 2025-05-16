import os
import requests
import json
from datetime import datetime

def fetch_current_bitcoin_price():
    """
    Fetch the current Bitcoin price and related metrics from CoinGecko API.
    """
    try:
        print("Fetching current Bitcoin price...")
        current_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
        current_response = requests.get(current_url, timeout=10)
        if current_response.status_code == 200:
            current_data = current_response.json()
            if 'bitcoin' in current_data:
                current_price = {
                    'price': current_data['bitcoin']['usd'],
                    'market_cap': current_data['bitcoin']['usd_market_cap'],
                    'vol_24h': current_data['bitcoin']['usd_24h_vol'],
                    'change_24h': current_data['bitcoin']['usd_24h_change'],
                    'timestamp': datetime.now().isoformat()
                }
                print(f"Current Bitcoin price: ${current_price['price']:,.2f}")
                
                # Ensure data directory exists
                os.makedirs('data', exist_ok=True)
                
                # Save current price data for dashboard
                with open('data/current_price.json', 'w') as f:
                    json.dump(current_price, f)
                return current_price
        else:
            print(f"Could not fetch current price: {current_response.status_code}")
    except Exception as e:
        print(f"Error fetching current price: {str(e)}")
    return None

if __name__ == "__main__":
    current_price = fetch_current_bitcoin_price()
    if current_price:
        print(f"Successfully saved current price data: ${current_price['price']:,.2f}")
        print(f"24h Change: {current_price['change_24h']:.2f}%")
        print(f"Market Cap: ${current_price['market_cap'] / 1_000_000_000:.2f}B")
    else:
        print("Failed to fetch current price data") 