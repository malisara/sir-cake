from users.models import AnonymousUser
from .models import BasketItem


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
