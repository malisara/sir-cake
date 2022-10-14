from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from seller.models import Item, OrderPackage
from users.models import AnonymousUser


class Basket(models.Model):
    item_to_buy = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    buyer_anon = models.ForeignKey(
        AnonymousUser, on_delete=models.CASCADE, blank=True, null=True)
    order_package = models.ForeignKey(
        OrderPackage, on_delete=models.CASCADE)
