from django.contrib import admin

from supermarkets_data.models import BritishOnlineSupermarketData, TescoData, AmazonData

# Register your models here.
admin.site.register(TescoData)
admin.site.register(AmazonData)
admin.site.register(BritishOnlineSupermarketData)