from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect

from seller.models import Item, Order
from sir_cake.utils import all_products_context
from store.models import BasketItem
from .forms import BasketItemForm
from .models import AnonymousUser
from .utils import (add_items_to_basket_or_redirect,
                    anonymous_user_without_session,
                    anonymous_user_with_saved_session,
                    get_number_reserved_items_in_preorders)


def store(request):
    # TODO change context
    if request.method == "POST":
        redirect_or_none = add_items_to_basket_or_redirect(request)
        if redirect_or_none is not None:
            return redirect(redirect_or_none)

    context = all_products_context(request)
    context['all_categories'] = Item.CATEGORIES_CHOICES
    return render(request, 'store/store.html', context)


def choose_purchasing_mode(request):
    if request.method == 'POST':
        if anonymous_user_without_session(request):
            request.session.create()
            AnonymousUser.objects.create(
                session_id=request.session.session_key)
        return redirect('store')
    return render(request, 'store/choose_purchasing_mode.html')


def store_item_detail(request, pk):
    try:
        item = Item.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    quanity_form = BasketItemForm(item.quantity -
                                  get_number_reserved_items_in_preorders(
                                      item))
    if request.method == 'POST':
        redirect_or_none = add_items_to_basket_or_redirect(request)
        if redirect_or_none != None:
            return redirect(redirect_or_none)
    return render(request, 'store/store-item-detail.html',
                  {'item': item, 'quanity_form': quanity_form})


def shopping_bag(request):
    if anonymous_user_without_session(request):
        return redirect('choose_purchasing_mode')

    preorder = _get_preorder(request)
    context = {'step': 1}

    if preorder is not None:
        basket_items = BasketItem.objects.filter(order=preorder)

        # Add max quantity to forms
        forms = []
        for basket_item in basket_items:
            max_quantity_to_buy = _get_max_quantity_to_buy(basket_item)
            forms.append(BasketItemForm(
                max_quantity_to_buy, instance=basket_item))

        context['zip_bag_form'] = zip(basket_items, forms)

        if request.method == "POST":
            if request.POST['action'] == "pay":
                _change_basket_item_quantity(request, preorder)
            elif request.POST['action'] == "cancel":
                BasketItem.objects.filter(order=preorder).delete()
                preorder.delete()
                messages.success(request, "Your shopping bag is deleted")
                return redirect('store')
            else:  # delete one item in basket
                item_pk = request.POST.get('action')
                BasketItem.objects.get(id=item_pk).delete()
                messages.success(request, "Item deleted")
                return redirect('shopping_bag')
    else:
        basket_items = None
    context['basket_items'] = basket_items
    return render(request, 'store/shopping-bag.html', context)


def _get_preorder(request):
    try:
        if request.user.is_anonymous:
            return Order.objects.get(
                status='preorder',
                buyer_anon=anonymous_user_with_saved_session(request))
        else:
            return Order.objects.get(status='preorder', buyer=request.user)
    except ObjectDoesNotExist:
        return None


def _get_max_quantity_to_buy(user_basket_item):
    user_item = user_basket_item.item_to_buy
    num_reserved_items = get_number_reserved_items_in_preorders(user_item)
    return user_item.quantity - num_reserved_items + user_basket_item.quantity


def _change_basket_item_quantity(request, preorder):
    items_pk = request.POST.getlist('item_pk')
    quantities_to_buy = request.POST.getlist('quantity')
    for item_pk, quantity_to_buy in zip(items_pk, quantities_to_buy):
        basket_item = BasketItem.objects.get(id=item_pk, order=preorder)

        if basket_item.item_to_buy.quantity - \
                get_number_reserved_items_in_preorders(basket_item) + \
                basket_item.quantity >= quantity_to_buy:
            basket_item.quantity = quantity_to_buy
            basket_item.save()
        else:
            messages.error(
                request,
                f"Not enough '{basket_item.item_to_buy}' items in store.")
