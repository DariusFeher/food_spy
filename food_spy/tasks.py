from background_task import background
from django.core.mail import send_mail


@background
def send_notif_email():
    print("INSIDE")
    send_mail(
        'TEST EMAIL - REPETITIVE',
        'TEST MESSAGE...',
        'teamfoodspy@gmail.com',
        ['feherdarius7@gmail.com'],
    )
    print("HERE")
    return 'Email sent!'