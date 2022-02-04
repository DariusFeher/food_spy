from unicodedata import name
from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from . import views

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('activate-user/<uidb64>/<token>', views.activate_user, name="activate"),
    path('resend-link/', views.get_new_activation_link, name="resend_activation"),
    path('request-reset-password', views.request_reset_password, name="request_new_password"),
    path('reset-password/<uidb64>/<token>', views.reset_password, name="reset_password"),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]