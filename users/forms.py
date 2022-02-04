from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _

from .models import Account


class CreateUserForm(UserCreationForm):
    username = forms.CharField(label=_('Username'))
    email = forms.EmailField(label=_('Email'), max_length=255)
    password1 = forms.CharField(label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'})
    )
    password2 = forms.CharField(label=_('Re-enter Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'})
    )
    class Meta:
        model = Account
        fields = ["username", "email", "password1", "password2"]
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5:
            raise ValidationError(_("The username should contain at least 5 characters."))
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            if Account.objects.get(email=email):
                raise ValidationError(_("Account with this Email already exists."))
        except:
            pass
        return email

class LoginUserForm(ModelForm):
    username = forms.CharField(label=_('Username or Email'))
    password1 = forms.CharField(label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'off','data-toggle': 'password'})
    )
    
    class Meta:
        model = Account
        fields = ["username", "password1"]

class RequestActivationLinkOrPassword(forms.Form):
    email = forms.CharField()

class ResetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        for fieldname in ['new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None
