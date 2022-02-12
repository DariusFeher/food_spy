"""food_spy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import deleteRecipe, homePage, get_recipe_ingredients_prices, save_and_display_recipes, recipe_price_comparison
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', homePage, name='home'),
    path('get_prices/', get_recipe_ingredients_prices, name='get_recipe_ingredients_prices'),
    path('myrecipes/', save_and_display_recipes, name='my_recipes'),
    path('myrecipes/<pk>/', recipe_price_comparison, name='recipe_price_comparison'),
    path('myrecipes/<pk>/delete', deleteRecipe, name='delete_recipe'),
    path('', include("users.urls")),
    path('accounts/', include('allauth.urls')),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
