from django.db import models
from django.core.validators import MinValueValidator

from seller.models import Item, Order


class BasketItem(models.Model):
    item_to_buy = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
