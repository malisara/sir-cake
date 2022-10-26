from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from seller.models import Item, Order
from users.models import AnonymousUser
from .models import BasketItem


def add_one_item_to_basket(request):

    if anonymous_user_without_session(request):
        return 'choose_purchasing_mode'

    try:
        item_to_buy = Item.objects.get(id=request.POST.get('item_pk'))
    except ObjectDoesNotExist:
        messages.error(request, "Item does not exist")
        return 'store'

    # Check how many items are 'reserved'
    num_reserved_items = 0
    for basket_instance in BasketItem.objects.filter(item_to_buy=item_to_buy):
        num_reserved_items += basket_instance.quantity

    if item_to_buy.quantity - num_reserved_items <= 0:
        messages.error(request, "Item out of stock")
        return 'store'

    if request.user.is_anonymous:
        _add_item_to_basket_create_order_anonymous_user(
            _get_user_with_saved_session(request), item_to_buy)
    else:
        _add_item_to_basket_create_order_user(request.user, item_to_buy)
    messages.success(request, "Item added to the basket")


def anonymous_user_without_session(request):
    return request.session.session_key is None


def _get_user_with_saved_session(request):
    return AnonymousUser.objects.get(session_id=request.session.session_key)


def _add_item_to_basket_create_order_user(user, item):
    try:
        order = Order.objects.get(buyer=user, status='preorder')
    except ObjectDoesNotExist:
        order = Order.objects.create(buyer=user, status="preorder")

    try:  # Item already in the basket -> increase quantity
        additional_item = BasketItem.objects.get(item_to_buy=item, order=order)
        additional_item.quantity += 1
        additional_item.save()
    except ObjectDoesNotExist:
        BasketItem.objects.create(item_to_buy=item, quantity=1, order=order)


def _add_item_to_basket_create_order_anonymous_user(anon_user, item):
    try:
        order = Order.objects.get(buyer_anon=anon_user, status='preorder')
    except ObjectDoesNotExist:
        order = Order.objects.create(buyer_anon=anon_user, status="preorder")

    try:
        additional_item = BasketItem.objects.get(order=order, item_to_buy=item)
        additional_item.quantity += 1
        additional_item.save()
    except ObjectDoesNotExist:
        BasketItem.objects.create(item_to_buy=item, quantity=1, order=order)
