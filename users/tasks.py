from background_task import background
from django.conf import settings
from django.contrib.sites.models import Site
# from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import (DjangoUnicodeDecodeError, force_bytes,
                                   force_str, force_text)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import Account
from .utils import generate_token


@background
def send_activation_email(user_pk):
    print(user_pk)
    user = Account.objects.get(pk=user_pk)
    current_site = Site.objects.get_current().domain
    email_subject = 'Please activate your account!'
    print(user.pk)
    print(user.username)
    print(user.email)
    email_body = render_to_string('accounts/activate.html', {
        'user': user.username,
        'domain': str(current_site).rstrip("/"),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    email = EmailMessage(subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_FROM_USER,
                to=[user.email])
    email.send()
    return "Activation email sent."

@background
def send_reset_password_email(user_pk):
    user = Account.objects.get(pk=user_pk)
    current_site = Site.objects.get_current().domain
    email_subject = 'Password reset for user ' + user.username
    email_body = render_to_string('accounts/password_reset_email.html', {
        'user': user.username,
        'domain': str(current_site).rstrip("/"),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    email = EmailMessage(subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_FROM_USER,
                to=[user.email])
    email.send()
    return "Reset password email sent."
