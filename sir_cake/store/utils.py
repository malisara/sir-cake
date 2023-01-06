from django.core.exceptions import ObjectDoesNotExist

from seller.utils import total_order_price
from users.models import AnonymousUser
from .models import BasketItem, Order


def get_number_reserved_items_in_preorders(item_to_buy):
    num_reserved_items = 0
    for basket_item in BasketItem.objects.filter(
            item_to_buy=item_to_buy, order__status=Order.Status.PREORDER):
        num_reserved_items += basket_item.quantity
    return num_reserved_items


def anonymous_user_without_session(request):
    return request.session.session_key is None


def anonymous_user_with_saved_session(request):
    return AnonymousUser.objects.get(session_id=request.session.session_key)


def get_items_and_prices_and_order_sum(shopping_bag):
    items_and_prices = []

    for item in shopping_bag:
        total_price_one_item = item.quantity * item.item_to_buy.price
        items_and_prices.append((item, total_price_one_item))

    return {
        'items_and_prices': items_and_prices,
        'total_price_all_items': total_order_price(shopping_bag),
    }


def get_preorder_or_none(request):
    try:
        if request.user.is_anonymous:
            return Order.objects.get(
                status=Order.Status.PREORDER,
                buyer_anon=anonymous_user_with_saved_session(request))
        else:
            return Order.objects.get(status=Order.Status.PREORDER,
                                     buyer=request.user)
    except ObjectDoesNotExist:
        return None


def user_has_items_in_basket_context_processor(request):
    return {'user_has_items_in_basket':
            get_preorder_or_none(request) is not None}
