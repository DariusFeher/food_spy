from django.contrib import admin

from .models import BritishOnlineSupermarketProduct

# Register your models here.
class BritishOnlineSupermarketProductAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated',)

admin.site.register(BritishOnlineSupermarketProduct, BritishOnlineSupermarketProductAdmin)