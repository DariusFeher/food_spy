from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class TescoData(models.Model):
   protected_tokens = PickledObjectField()
   products_data = PickledObjectField()