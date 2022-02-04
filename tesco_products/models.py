from django.db import models

# Create your models here.

currencies = [
            ('1', ('$')),
            ('2', ('€')),
            ('3', ('£'))
]

class TescoProduct(models.Model):
    short_name = models.CharField(max_length=200)
    price = models.FloatField()
    currency = models.CharField(max_length=20, choices=currencies)
    full_name = models.CharField(max_length=300)
    link = models.CharField(max_length=2000)

    def __str__(self) -> str:
        return str(self.full_name)

