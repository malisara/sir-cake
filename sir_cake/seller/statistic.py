from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.utils import timezone

from .models import Item, Order
from .utils import total_order_price
from store.models import BasketItem
from users.models import AnonymousUser


def inventory_value():
    inventory_value_dict = Item.objects.aggregate(
        inventory_value=Sum(F('quantity') * F('price')))
    return inventory_value_dict['inventory_value']


def total_sales():
    sold_items = _sold_basket_items().aggregate(
        value=Sum(F('quantity') * F('item_to_buy__price')))
    return sold_items['value']


def best_sellers():
    # Top 5 best sold items
    top_five_basket_items = _sold_basket_items().values('item_to_buy').annotate(
        number_items=Sum('quantity')).order_by('-number_items')[:5]

    items = []
    categories = []
    number_items_sold = []
    total_sales = []

    for basket_item in top_five_basket_items:
        item = Item.objects.get(id=basket_item['item_to_buy'])
        items.append(item)
        categories.append(Item.SHORT_CATEGORY_TO_NAME[item.category])
        number_sold = basket_item['number_items']
        number_items_sold.append(number_sold)
        total_sales.append(number_sold * item.price)

    return zip(items, categories, number_items_sold, total_sales)


def _sold_basket_items():
    return BasketItem.objects.exclude(
        order__status=Order.Status.PREORDER)


def number_customers():
    return _number_registred_users() + _number_unregistred_users()


def last_month_statistic():
    # Newly registred users and sold items in € in last 30days
    time_delta_last_month = timezone.now()-timezone.timedelta(days=30)
    orders = Order.objects.exclude(status=Order.Status.PREORDER).filter(
        order_date__gte=time_delta_last_month)

    sales = 0
    for order in orders:
        basket_item = BasketItem.objects.filter(order=order)
        sales += total_order_price(basket_item)

    registred_users = User.objects.filter(
        date_joined__gte=time_delta_last_month).count()

    return sales, registred_users


def _number_registred_users():
    return User.objects.count()


def _number_unregistred_users():
    return AnonymousUser.objects.count()
