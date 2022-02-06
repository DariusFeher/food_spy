
from tabnanny import verbose
from .tasks import send_notif_email
from background_task.models import Task
from django.shortcuts import render
from django.core.mail import send_mail
from tesco_products.tasks import update_tesco_products_db
import requests, lxml


def homePage(request):
    # if len(Task.objects.filter(verbose_name="send_notif_email")) == 0:
    #     send_notif_email(repeat=2, verbose_name="send_notif_email")
    # send_mail(
    #     'TEST EMAIL - REPETITIVE',
    #     'TEST MESSAGE...',
    #     'teamfoodspy@gmail.com',
    #     ['feherdarius7@gmail.com'],
    # )
    
    if len(Task.objects.filter(verbose_name="update_tesco_db")) == 0:
        update_tesco_products_db(repeat=Task.DAILY, verbose_name="update_tesco_db")

    if request.method == 'GET':
        print("START REQUEST HOMEPAGE")
        category_urls = {
            'fresh-food' : 'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all?include-children=true',
            'bakery' : 'https://www.tesco.com/groceries/en-GB/shop/bakery/all',
            'frozen-food' : 'https://www.tesco.com/groceries/en-GB/shop/frozen-food/all',
            'food-cupboard' : 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all',
            'drinks' : 'https://www.tesco.com/groceries/en-GB/shop/drinks/all',
            'easter' : 'https://www.tesco.com/groceries/en-GB/shop/easter/all',
            'pet-food' : 'https://www.tesco.com/groceries/en-GB/shop/pets/all',
        }
        headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        params = {
            'page' : 1
        }

        html = requests.get(category_urls['fresh-food'], headers=headers, params=params).text
        print("END REQUEST HOMPAGE")
        return render(request, 'home.html')