from background_task import background
from django.core.mail import send_mail

@background(queue='main-queue')
def send_notif_email():
    return 'Email sent!'