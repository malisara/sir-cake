from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from seller.models import Item, OrderPackage
from users.models import AnonymousUser
from .models import Basket


def add_one_item_basket(request, context):
    # Anonymous user without session
    if request.session.session_key is None:
        return 'continue_purchase'

    basket = []
    if request.user.is_anonymous:
        anon_user = get_user_with_saved_session(request)
        basket = Basket.objects.filter(buyer_anon=anon_user)
    else:
        user = request.user
        basket = Basket.objects.filter(buyer=user)

    # For navbar shopping-bag icon
    context['items_in_basket'] = len(basket)

    try:
        item_to_buy = Item.objects.get(id=request.POST.get('item_pk'))
    except ObjectDoesNotExist:
        # TODO: different message?
        messages.error(request, "Item out of stock")
        return 'store'

    # Check how many items are 'reserved'
    num_reserved_items = 0
    for basket_instance in Basket.objects.filter(item_to_buy=item_to_buy):
        num_reserved_items += basket_instance.quantity

    if item_to_buy.quantity - num_reserved_items <= 0:
        messages.error(request, "Item out of stock")
        return 'store'

    if request.user.is_anonymous:
        order_package_basket_anon(anon_user, item_to_buy)
        messages.success(request, "Item added to the basket")
    else:
        order_package_basket(user, item_to_buy)
        messages.success(request, "Item added to the basket")


def get_user_with_saved_session(request):
    return AnonymousUser.objects.get(session_id=request.session.session_key)


def order_package_basket(user, item):
    # User doesn't have order package yet
    if len(OrderPackage.objects.filter(buyer=user, status='preorder')) == 0:
        OrderPackage.objects.create(buyer=user, status="preorder")

    try:  # Item already in the basket -> increase quantity
        additiomal_item = Basket.objects.get(item_to_buy=item, buyer=user)
        additiomal_item.quantity += 1
        additiomal_item.save()

    except ObjectDoesNotExist:
        Basket.objects.create(item_to_buy=item, quantity=1, buyer=user,
                              order_package=OrderPackage.objects.get(status="preorder", buyer=user))


def order_package_basket_anon(anon_user, item):
    if len(OrderPackage.objects.filter(buyer_anon=anon_user, status='preorder')) == 0:
        OrderPackage.objects.create(buyer_anon=anon_user, status="preorder")
    try:
        additiomal_item = Basket.objects.get(
            buyer_anon=anon_user, item_to_buy=item)
        additiomal_item.quantity += 1
        additiomal_item.save()

    except ObjectDoesNotExist:
        Basket.objects.create(item_to_buy=item, quantity=1, buyer_anon=anon_user,
                              order_package=OrderPackage.objects.get(status="preorder", buyer_anon=anon_user))
