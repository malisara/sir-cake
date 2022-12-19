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


class AnonymousUserUpdateNamesForm(forms.ModelForm):
    class Meta:
        model = AnonymousUser
        fields = ['first_name', 'last_name']


class UserUpdateNamesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
