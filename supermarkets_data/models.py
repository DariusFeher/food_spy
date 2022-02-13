from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class TescoData(models.Model):
   protected_tokens = JSONField()
   products_data = JSONField()

class AmazonData(models.Model):
   protected_tokens = JSONField()
   products_data = JSONField()
   products_entities = JSONField()