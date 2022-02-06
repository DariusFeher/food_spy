from background_task import background
from django.core.mail import send_mail

@background()
def send_notif_email():
    return 'Email sent!'