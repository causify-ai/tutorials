import requests

def get_bitcoin_price(api_url='https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def check_threshold(current_price, threshold, direction='above'):
    if current_price is None:
        return False
    if direction == 'above':
        return current_price > threshold
    elif direction == 'below':
        return current_price < threshold
    else:
        raise ValueError("direction must be 'above' or 'below'")

def send_alert(message):
    print(f"[ALERT] 🚨 {message}")

def fetch_and_alert(api_url, threshold, direction='above'):
    price = get_bitcoin_price(api_url)
    if check_threshold(price, threshold, direction):
        send_alert(f"Bitcoin price is {direction} ${threshold}!")
    return price
