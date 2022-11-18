from django import forms
from .models import BasketItem
from django.core.validators import MinValueValidator, MaxValueValidator


class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem
        fields = ['quantity']

    def __init__(self, inventory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide field label
        self.fields['quantity'].label = ""
        self.fields['quantity'].validators = [
            MinValueValidator(1), MaxValueValidator(inventory)]
        self.fields['quantity'].widget.attrs['placeholder'] = 'quantity'
        # HTML validators
        self.fields['quantity'].widget.attrs['min'] = '1'
        self.fields['quantity'].widget.attrs['max'] = f'{inventory}'
#        widget=forms.TextInput(attrs={'placeholder': 'Search'}
