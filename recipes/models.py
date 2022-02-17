from enum import auto
from django.db import models
from django.forms import DateTimeField
from users.models import Account
from django.contrib.postgres.fields import JSONField

# Create your models here.

class Recipe(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    products_tesco = JSONField()
    products_british_online_supermarket = JSONField()
    last_updated = models.DateTimeField(verbose_name='last_updated', auto_now=True)

    def __str__(self) -> str:
        return 'Recipe ' + str(self.pk)