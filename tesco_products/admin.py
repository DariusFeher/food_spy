from django.contrib import admin
from .models import TescoProduct
from django.db import models

# # Register your models here.
class TescoProductAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated',)

admin.site.register(TescoProduct, TescoProductAdmin)