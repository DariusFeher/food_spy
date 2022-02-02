
from .tasks import send_notif_email
from background_task.models import Task
from django.shortcuts import render

def homePage(request):
    if len(Task.objects.filter(verbose_name="send_notif_email")) == 0:
        send_notif_email(repeat=10, verbose_name="send_notif_email")
    if request.method == 'GET':
        return render(request, 'home.html')