from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from users.models import AnonymousUser, ShippingAddress


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in self.Meta.fields:
            self.fields[fieldname].help_text = None


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['street_name', 'house_number', 'city', 'country', ]


class AnonShippingAddressForm(forms.ModelForm):
    class Meta:
        model = AnonymousUser
        fields = ['name', 'last_name']


class UserUpdateNamesForm(forms.Form):
    name = forms.CharField(label='Name', max_length=40)
    last_name = forms.CharField(label='Last name', max_length=40)
