from background_task import background
from django.core.mail import send_mail
from post_office.connections import connections



@background()
def send_notif_email():
    print("INSIDE")
    
    print("HERE")
    return 'Email sent!'