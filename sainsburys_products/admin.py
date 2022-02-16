from django.contrib import admin

from sainsburys_products.models import SainsburysProduct

# Register your models here.
class SainsburysProductAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated',)

admin.site.register(SainsburysProduct, SainsburysProductAdmin)