from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class TescoData(models.Model):
   protected_tokens = JSONField()
   products_data = JSONField()