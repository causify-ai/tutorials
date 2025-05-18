import requests
import time
from datetime import datetime
import json

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
    target_points = 30
    current_points = 0
    print(f"Starting Bitcoin price collection. Target: {target_points} data points")
    print("Will take approximately 15 minutes (30 seconds between points)")
    print("Press Ctrl+C to stop early...")
    
    try:
        while current_points < target_points:
            price_data = fetch_bitcoin_price()
            if price_data:
                # Append to JSON file
                with open('btc_prices.json', 'a') as f:
                    json.dump(price_data, f)
                    f.write('\n')
                current_points += 1
                print(f"Progress: {current_points}/{target_points} data points collected")
            time.sleep(30)  # Fetch every 30 seconds to avoid rate limiting
        print("\nData collection complete! You can now run the visualization notebook.")
    except KeyboardInterrupt:
        print(f"\nStopped price collection. Collected {current_points} data points.")
        if current_points > 0:
            print("You can still run the visualization with the collected data.")
