import requests
import time
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        price = data['bitcoin']['usd']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Bitcoin Price: ${price}")
        return {'timestamp': timestamp, 'price': price}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price: {e}")
        return None

if __name__ == "__main__":
    while True:
        fetch_bitcoin_price()
        time.sleep(10)  # Fetch every 10 seconds
