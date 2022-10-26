from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from seller.models import Item, Order
from users.models import AnonymousUser


class BasketItem(models.Model):
    item_to_buy = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
