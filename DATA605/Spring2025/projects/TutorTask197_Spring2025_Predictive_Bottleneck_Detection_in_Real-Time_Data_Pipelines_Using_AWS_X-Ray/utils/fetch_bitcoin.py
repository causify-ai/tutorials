import requests

def fetch_bitcoin_price():
    """
    Fetch the current Bitcoin price from CoinGecko API.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()  # Raise error for bad responses
    data = response.json()
    return data['bitcoin']['usd']
