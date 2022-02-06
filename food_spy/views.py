
from tabnanny import verbose
from .tasks import send_notif_email
from background_task.models import Task
from django.shortcuts import render
from django.core.mail import send_mail
from tesco_products.tasks import update_tesco_products_db

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
        return render(request, 'home.html')