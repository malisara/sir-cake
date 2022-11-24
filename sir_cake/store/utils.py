from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from seller.models import Item, Order
from users.models import AnonymousUser
from .models import BasketItem


def add_items_to_basket_or_redirect(request,
                                    basket_item_form,
                                    item,
                                    custom_redirect):
    # This function is only called with POST requests
    if anonymous_user_without_session(request):
        return 'choose_purchasing_mode'

    if not basket_item_form.is_valid():
        errors = basket_item_form.errors.as_data().get('quantity', [])
        for error in errors:
            error_string = " ".join(error.messages)
            messages.error(request, error_string)
            # If item is out of stock, return user to 'store' view
            if 'Item out of stock' in error_string:
                custom_redirect = 'store'
        return custom_redirect


def _add_more_items_to_basket(request, item_to_buy,
                              available_quantity):

    quantity_to_buy = int(request.POST.get('quantity'))

    if available_quantity == 0:
        messages.error(request, "Item is sold out.")
        return 'store'
    elif available_quantity < quantity_to_buy:
        messages.error(request, "Not enough items in store.")
        return 'store'
        # TODO refresh?

    order = _get_order(request)
    try:  # Item already in the basket -> change quantity
        item_in_basket = BasketItem.objects.get(
            item_to_buy=item_to_buy, order=order)
        item_in_basket.quantity += quantity_to_buy
        item_in_basket.save()
    except ObjectDoesNotExist:
        BasketItem.objects.create(
            item_to_buy=item_to_buy, quantity=quantity_to_buy, order=order)
    messages.success(request, "Item added to the basket")
    return 'store'
    # TODO refresh?


def _get_order(request):
    if request.user.is_anonymous:
        return _create_and_get_order_anonymous_user(
            anonymous_user_with_saved_session(request))
    else:
        return _create_and_get_order_user(request.user)


def get_number_reserved_items_in_preorders(item_to_buy):
    num_reserved_items = 0
    for basket_item in BasketItem.objects.filter(item_to_buy=item_to_buy,
                                                 order__status='preorder'):
        num_reserved_items += basket_item.quantity
    return num_reserved_items


def anonymous_user_without_session(request):
    return request.session.session_key is None


def anonymous_user_with_saved_session(request):
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
