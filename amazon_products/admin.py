from django.contrib import admin
from .models import AmazonProduct

# Register your models here.
class AmazonProductAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated',)

admin.site.register(AmazonProduct, AmazonProductAdmin)