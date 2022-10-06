from django.contrib.auth.models import User
from django.db import models
from django.contrib.sessions.models import Session


class AnonymousUser(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, default=None)
    last_name = models.CharField(max_length=40, default=None)


class ShippingAddress(models.Model):
    street_name = models.CharField(max_length=200)
    house_number = models.CharField(max_length=5)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None, blank=True, null=True)
    user_anon = models.ForeignKey(
        AnonymousUser, on_delete=models.CASCADE, default=None, blank=True, null=True)


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)
