from django import forms
from .models import BasketItem
from django.core.validators import MinValueValidator, MaxValueValidator


class BasketForm(forms.ModelForm):
    class Meta:
        model = BasketItem
        fields = ['quantity']

    def __init__(self, inventory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide field lable
        self.fields['quantity'].label = ""
        self.fields['quantity'].validators = [
            MinValueValidator(0), MaxValueValidator(inventory)]
        # HTML validators
        self.fields['quantity'].widget.attrs['min'] = '0'
        self.fields['quantity'].widget.attrs['max'] = f'{inventory}'
