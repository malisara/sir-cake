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


def sales_status_ratio():
    order = Order.objects.exclude(status=Order.Status.PREORDER)

    return {'status': [Order.Status.UNSENT, Order.Status.SHIPPED],
            'quantity': [order.filter(status=Order.Status.PAID).count(),
                         order.filter(status=Order.Status.SHIPPED).count()]}


def sold_per_category():
    categories_and_sales = {'category': [], 'total_sales': []}
    category_price_query_set = _sold_basket_items().values(
        'item_to_buy__category').annotate(value_sold=Sum(
            F('quantity') * F('item_to_buy__price')))

    for item in category_price_query_set:
        categories_and_sales['category'].append(
            Item.SHORT_CATEGORY_TO_NAME[item['item_to_buy__category']])
        categories_and_sales['total_sales'].append(item['value_sold'])
    return categories_and_sales


def sales_graph():
    sales = {'date': [], 'sales': []}
    orders = Order.objects.exclude(status=Order.Status.PREORDER)
    for order in orders:
        value = total_order_price(BasketItem.objects.filter(order=order))
        date = order.order_date.strftime("%d.%m.%y")

        try:
            index = sales['date'].index(date)
            sales['sales'][index] += value
        except ValueError:
            sales['date'].append(date)
            sales['sales'].append(value)
    return sales


def user_registration_statistic():
    '''This function return register statistic for last 100 users'''
    registrations = {'date': [], 'number_users': []}
    last_hundred_users = User.objects.all()[:100]

    for user in last_hundred_users:
        date_joined = user.date_joined.strftime("%d.%m.%y")
        try:
            index = registrations['date'].index(date_joined)
            registrations['number_users'][index] += 1
        except ValueError:
            registrations['date'].append(date_joined)
            registrations['number_users'].append(1)
    return registrations


def un_registred_users():
    return {'user_status': ['registered', 'unregistered'],
            'number_users': [_number_registred_users(),
                             _number_unregistred_users()]}
