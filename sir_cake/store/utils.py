from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from seller.models import Item, Order
from users.models import AnonymousUser
from .models import BasketItem


def add_one_item_to_basket_or_redirect(request):
    # This function is only called with POST requests

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
        messages.error(
            request, "Not enough items in stock given the selected quantity")
        return 'store'

    if request.user.is_anonymous:
        order = _create_and_get_order_anonymous_user(
            get_user_with_saved_session(request))
    else:
        order = _create_and_get_order_user(request.user)

    try:  # Item already in the basket -> increase quantity
        additional_item = BasketItem.objects.get(
            item_to_buy=item_to_buy, order=order)
        additional_item.quantity += 1
        additional_item.save()
    except ObjectDoesNotExist:
        BasketItem.objects.create(
            item_to_buy=item_to_buy, quantity=1, order=order)
    messages.success(request, "Item added to the basket")


def anonymous_user_without_session(request):
    return request.session.session_key is None


def get_user_with_saved_session(request):
    return AnonymousUser.objects.get(session_id=request.session.session_key)


def _create_and_get_order_user(user):
    try:
        return Order.objects.get(buyer=user, status='preorder')
    except ObjectDoesNotExist:
        return Order.objects.create(buyer=user, status="preorder")


def _create_and_get_order_anonymous_user(anon_user):
    try:
        return Order.objects.get(buyer_anon=anon_user, status='preorder')
    except ObjectDoesNotExist:
        return Order.objects.create(buyer_anon=anon_user, status="preorder")
