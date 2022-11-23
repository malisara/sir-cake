from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import BasketItem


class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem
        fields = ['quantity']

    def __init__(self, max_quantity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_quantity = max_quantity
        # Hide field label
        self.fields['quantity'].label = ""
        self.fields['quantity'].validators = [
            MinValueValidator(1), MaxValueValidator(max_quantity)]
        self.fields['quantity'].widget.attrs['value'] = 1
        # HTML validators
        self.fields['quantity'].widget.attrs['min'] = 1
        self.fields['quantity'].widget.attrs['max'] = max_quantity

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        if self.max_quantity < data:
            raise ValidationError("Not enough items in stock.")
        return data
