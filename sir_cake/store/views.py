from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect

from seller.models import Item, Order
from sir_cake.utils import all_products_context
from store.models import BasketItem
from .forms import BasketForm
from .models import AnonymousUser
from .utils import (add_one_item_to_basket_or_redirect,
                    anonymous_user_without_session,
                    get_user_with_saved_session)


def store(request):
    if request.method == "POST":
        redirect_or_none = add_one_item_to_basket_or_redirect(request)
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

    if request.method == 'POST':
        redirect_or_none = add_one_item_to_basket_or_redirect(request)
        if redirect_or_none != None:
            return redirect(redirect_or_none)
    return render(request, 'store/store-item-detail.html', {'item': item})


def shopping_bag(request):
    if anonymous_user_without_session(request):
        return redirect('choose_purchasing_mode')
    if request.user.is_anonymous:
        shopping_bag, preorder = _get_shopping_bag_preorder_anonymous_user(
            request)
    else:
        shopping_bag, preorder = _get_shopping_bag_preorder_user(request)
    context = {'shopping_bag': shopping_bag}

    if shopping_bag is not None:
        # Add max quantity to forms
        forms = []
        for bag_item in shopping_bag:
            max_quantity_to_buy = _get_max_quantity_to_buy(bag_item)
            forms.append(BasketForm(max_quantity_to_buy, instance=bag_item))

            if max_quantity_to_buy <= 0:
                bag_item.delete()
                messages.error(request,
                               f"Item {bag_item.item_to_buy} out of stock.")
        context['zip_bag_form'] = zip(shopping_bag, forms)

        if request.method == "POST":
            if request.POST['action'] == "pay":
                _change_basket_item_quantity(request, preorder)
            else:
                BasketItem.objects.filter(order=preorder).delete()
                preorder.delete()
                messages.success(request, "Your shopping bag is deleted")
                return redirect('store')

    return render(request, 'store/shopping-bag.html', context)


def _change_basket_item_quantity(request, preorder):
    items_pk = request.POST.getlist('item_pk')
    quantities_to_buy = request.POST.getlist('quantity')
    for item_pk, quantity_to_buy in zip(items_pk, quantities_to_buy):
        basket_item = BasketItem.objects.get(id=item_pk, order=preorder)
        basket_item.quantity = quantity_to_buy
        basket_item.save()


def _get_max_quantity_to_buy(bag_item):
    item = bag_item.item_to_buy
    num_reserved_items = 0
    for basket_item in BasketItem.objects.filter(item_to_buy=item):
        num_reserved_items += basket_item.quantity
    return item.quantity - num_reserved_items + bag_item.quantity


def _get_shopping_bag_preorder_anonymous_user(request):
    anonymous_user = get_user_with_saved_session(request)
    try:
        preorder = Order.objects.get(status='preorder',
                                     buyer_anon=anonymous_user)
        return BasketItem.objects.filter(order=preorder), preorder
    except ObjectDoesNotExist:
        return None, None


def _get_shopping_bag_preorder_user(request):
    try:
        preorder = Order.objects.get(status='preorder', buyer=request.user)
        return BasketItem.objects.filter(order=preorder), preorder
    except ObjectDoesNotExist:
        return None, None
