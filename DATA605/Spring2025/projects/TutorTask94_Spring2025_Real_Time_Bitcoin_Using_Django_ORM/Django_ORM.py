# -*- coding: utf-8 -*-
# **Data Ingesation**



Step 1 : Fetch Real-Time Price from CoinGecko API
"""

import requests
from django.core.management.base import BaseCommand
from tracker.models import BitcoinPrice

# Django custom command: `python manage.py fetch_prices`
class Command(BaseCommand):
    help = 'Fetch the latest Bitcoin price and store it in the database'

    def handle(self, *args, **kwargs):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

        try:
            response = requests.get(url)
            data = response.json()
            price = data['bitcoin']['usd']  # Extract price from JSON response

            if price:
                # Create a new database record with the current price
                BitcoinPrice.objects.create(price_usd=price)
                self.stdout.write(self.style.SUCCESS(f"Saved price: ${price}"))
            else:
                self.stdout.write(self.style.WARNING("Price data not found in API response"))
        except Exception as e:
            # Print error if something goes wrong
            self.stdout.write(self.style.ERROR(f"Error fetching price: {e}"))

"""# **Data Processing**

 Step 2 : Define the ORM Model for Bitcoin Price
"""

from django.db import models
from django.db.models import Avg
import numpy as np

# This model stores each Bitcoin price observation
class BitcoinPrice(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically adds current time when record is created
    price_usd = models.FloatField()  # Stores the price in USD

    def __str__(self):
        # Returns a readable string for each entry
        return f"{self.timestamp}: ${self.price_usd}"

    @classmethod
    def average_price(cls):
        # Calculates average price across all records
        return cls.objects.aggregate(Avg('price_usd'))['price_usd__avg']

    @classmethod
    def price_volatility(cls):
        # Calculates standard deviation (volatility) of all price values
        prices = list(cls.objects.values_list('price_usd', flat=True))
        return np.std(prices) if prices else 0

    @classmethod
    def latest_prices(cls, n=10):
        # Returns the latest `n` entries in chronological order
        return cls.objects.order_by('-timestamp')[:n][::-1]
