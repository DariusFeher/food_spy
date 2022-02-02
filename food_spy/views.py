
from .tasks import send_notif_email
from background_task.models import Task
from django.shortcuts import render
from django.core.mail import send_mail

def homePage(request):
    if len(Task.objects.filter(verbose_name="send_notif_email")) == 0:
        send_notif_email(repeat=2, verbose_name="send_notif_email")
    # send_mail(
    #     'TEST EMAIL - REPETITIVE',
    #     'TEST MESSAGE...',
    #     'teamfoodspy@gmail.com',
    #     ['feherdarius7@gmail.com'],
    # )
    if request.method == 'GET':
        return render(request, 'home.html')