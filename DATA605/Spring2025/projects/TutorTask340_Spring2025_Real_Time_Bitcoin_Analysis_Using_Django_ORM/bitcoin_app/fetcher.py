import requests
from .models import BitcoinPrice
from django.utils import timezone

def fetch_and_store_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        price = response.json()["bitcoin"]["usd"]
        BitcoinPrice.objects.create(timestamp=timezone.now(), price_usd=price)
    except Exception as e:
        print(f"Error fetching/storing price: {e}")
