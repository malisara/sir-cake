from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from PIL import Image

from .image_utils import crop_max_square
from users.models import AnonymousUser


class Item(models.Model):

    class Category:
        COOKIES = 'CO'
        CAKES = 'CA'
        ICE_CREAMS = 'I'
        ALL = 'ALL'

    CATEGORIES_CHOICES = [
        (Category.COOKIES, 'Cookies'),
        (Category.CAKES, 'Cakes'),
        (Category.ICE_CREAMS, 'Ice creams'),
        (Category.ALL, 'All Sweets'),
    ]

    SHORT_CATEGORY_TO_NAME = dict(CATEGORIES_CHOICES)

    title = models.CharField(max_length=50)
    # "Price in €" displayed as a field name in form
    price = models.FloatField("Price in €", default="0.00", validators=[
                              MinValueValidator(0.0)])
    description = models.TextField(max_length=100, null=True, blank=True)
    category = models.CharField(
        max_length=3,
        choices=CATEGORIES_CHOICES,
        default=Category.ALL,
    )
    image = models.ImageField(upload_to='product_pics')
    date_posted = models.DateTimeField(default=timezone.now)
    quantity = models.IntegerField(default=0, validators=[
        MinValueValidator(0.0)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assign_shorter_title()
        self.assign_category_full_name()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        img_cropped = crop_max_square(img)

        if img_cropped.height > 400:
            img_cropped.thumbnail((400, 400))

        img_cropped.save(self.image.path)

    def assign_shorter_title(self):

        if len(self.title) > 20:
            self.short_title = self.title[:17] + "..."
        else:
            self.short_title = self.title

    def assign_category_full_name(self):
        self.long_category = self.SHORT_CATEGORY_TO_NAME[self.category]


class Order(models.Model):

    class Status:
        PREORDER = 'preorder'
        PAID = 'paid'
        SHIPPED = 'shipped'
        UNSENT = 'unsent'
        ALL = 'all'

    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    buyer_anon = models.ForeignKey(
        AnonymousUser, on_delete=models.CASCADE, blank=True, null=True)
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10)
