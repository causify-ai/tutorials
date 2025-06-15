import requests

def get_bitcoin_price(api_url='https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'):
    """
    Fetch current Bitcoin price in USD from CoinGecko API.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def check_threshold(current_price, threshold, direction='above'):
    """
    Check if the price crosses a threshold.
    
    direction: 'above' or 'below'
    """
    if current_price is None:
        return False

    if direction == 'above':
        return current_price > threshold
    elif direction == 'below':
        return current_price < threshold
    else:
        raise ValueError("direction must be 'above' or 'below'")


def send_alert(message):
    """
    Simulate sending an alert (e.g., print, log, or future email/SMS).
    """
    print(f"[ALERT] 🚨 {message}")

