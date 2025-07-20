from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'address', 'password1', 'password2')

class LoginForm(forms.Form):
    username_or_phone = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
