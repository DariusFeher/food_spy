from django.contrib import admin

# Register your models here.
from .models import Recipe

class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated',)

# Register your models here.
admin.site.register(Recipe, RecipeAdmin)
