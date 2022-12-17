from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

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
        self.fields['quantity'].validators = [MinValueValidator(1)]
        # MaxValueValidator is performed in 'clean_quantity'.
        self.fields['quantity'].widget.attrs['value'] = 1
        # HTML validators
        self.fields['quantity'].widget.attrs['min'] = 1
        self.fields['quantity'].widget.attrs['max'] = max_quantity

    def clean_quantity(self):
        if self.max_quantity <= 0:
            raise ValidationError("Item out of stock.")
        data = self.cleaned_data['quantity']
        if self.max_quantity < data:
            raise ValidationError(
                (f"Not enough items in stock."
                 "Max available quantity is {self.max_quantity}."))
        return data


class PaymentForm(forms.Form):
    credit_card = forms.CharField(
        label='Credit card number', min_length=16, max_length=19)
    name = forms.CharField(label='Card holder name', max_length=15)
    cvv = forms.CharField(label='CVV', min_length=3, max_length=4)
    expire_date = forms.DateField(label='Expire date')

    def clean_credit_card(self):
        return _validate_cvv_and_credit_card(
            self.cleaned_data['credit_card'], 'credit card')

    def clean_cvv(self):
        return _validate_cvv_and_credit_card(
            self.cleaned_data['cvv'], 'cvv')


def _validate_cvv_and_credit_card(data, error_message):
    for char in data:
        try:
            int(char)
        except ValueError:
            raise ValidationError(
                f"Please enter a valid {error_message} number.")
    return data
