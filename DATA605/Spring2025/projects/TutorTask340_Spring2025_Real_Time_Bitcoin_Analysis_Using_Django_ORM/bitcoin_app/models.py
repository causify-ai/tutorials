from django.db import models

# Create your models here.
from django.db import models

class BitcoinPrice(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    price_usd = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - ${self.price_usd:.2f}"
