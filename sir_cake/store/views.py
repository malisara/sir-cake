from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect

from seller.models import Item, Order
from sir_cake.utils import all_products_context
from store.models import BasketItem
from .forms import BasketItemForm
from .models import AnonymousUser
from .utils import (anonymous_user_without_session,
                    anonymous_user_with_saved_session,
                    get_number_reserved_items_in_preorders)


def store(request):
    form = BasketItemForm(1)
    context = all_products_context(request)
    context['form'] = form
    context['all_categories'] = Item.CATEGORIES_CHOICES

    if request.method == "POST":
        item_pk = request.POST.get('item_pk', None)
        if item_pk is None:
            return HttpResponseBadRequest()
        try:
            item_pk = int(item_pk)
        except ValueError:
            return HttpResponseBadRequest()

        item = _get_item(item_pk)
        if item is None:
            return HttpResponseBadRequest()

        # We create a new form here to make sure there is a single item in
        # stock. We only ever add a single item here.
        post_form = BasketItemForm(_get_max_quantity_to_buy(
            item), data={'quantity': 1})
        redirect_ = _add_items_to_basket_or_redirect(request, post_form, item,
                                                     'store')
        if redirect_ is not None:
            return redirect(redirect_)

    return render(request, 'store/store.html', context)


def store_item_detail(request, pk):
    item = _get_item(pk)
    if item is None:
        return HttpResponseNotFound()

    if request.method == 'POST':
        post_form = BasketItemForm(_get_max_quantity_to_buy(item),
                                   data=request.POST)
        redirect_ = _add_items_to_basket_or_redirect(request, post_form, item,
                                                     'store_item_detail')
        if redirect_ is not None:
            if redirect_ == 'store_item_detail':
                return redirect('store_item_detail', pk=pk)
            return redirect(redirect_)

    form = BasketItemForm(_get_max_quantity_to_buy(item))
    return render(request, 'store/store-item-detail.html',
                  {'item': item, 'form': form})


def choose_purchasing_mode(request):
    if request.method == 'POST':
        if anonymous_user_without_session(request):
            request.session.create()
            AnonymousUser.objects.create(
                session_id=request.session.session_key)
        return redirect('store')
    return render(request, 'store/choose_purchasing_mode.html')


def shopping_bag(request):
    if anonymous_user_without_session(request):
        return redirect('choose_purchasing_mode')

    context = {'step': 1}
    preorder = _get_preorder_or_none(request)

    if preorder is None:
        # Shopping bag is empty.
        return render(request, 'store/shopping-bag.html', context)

    if request.method == "POST":
        if "action" not in request.POST:
            return HttpResponseBadRequest()
        if request.POST['action'] not in ["pay", "cancel"] and \
                not request.POST['action'].startswith("delete_"):
            return HttpResponseBadRequest()

    if request.method == "POST" and request.POST['action'].startswith("delete"):
        # Single item is deleted.
        try:
            delete_pk = int(request.POST.get('action').split('_')[1])
        except ValueError:
            return HttpResponseBadRequest()
        BasketItem.objects.get(id=delete_pk).delete()
        messages.success(request, "Item deleted")

    basket_items = BasketItem.objects.filter(order=preorder)

    if request.method == "POST" and request.POST['action'] == "cancel":
        # Whole basket is deleted.
        basket_items.delete()
        preorder.delete()
        messages.success(request, "Your shopping bag is deleted")
        return redirect('store')

    if request.method == "POST" and request.POST['action'] == "pay":
        if "quantity" in request.POST and \
                len(request.POST.getlist('quantity')) == len(basket_items):
            quantities = request.POST.getlist('quantity')
        else:
            return HttpResponseBadRequest()

    forms = []
    for i, basket_item in enumerate(basket_items):
        max_quantity = _get_max_quantity_to_buy_without_users_already_reserved(
            basket_item)
        if request.method == "POST" and request.POST['action'] == "pay":
            forms.append(BasketItemForm(max_quantity,
                                        data={'quantity': quantities[i]},
                                        instance=basket_item))
        else:
            forms.append(BasketItemForm(max_quantity, instance=basket_item))

    if request.method == "POST" and request.POST['action'] == "pay":
        # Proceed to checkout.
        for form in forms:
            if form.is_valid():
                form.save()
        # TODO: redirect to checkout.
        return redirect('store')

    context['items_and_forms'] = list(zip(basket_items, forms))
    return render(request, 'store/shopping-bag.html', context)


def _get_item(pk):
    try:
        return Item.objects.get(id=pk)
    except ObjectDoesNotExist:
        return None


def _get_max_quantity_to_buy_without_users_already_reserved(user_basket_item):
    return _get_max_quantity_to_buy(user_basket_item.item_to_buy) + \
        user_basket_item.quantity


def _get_max_quantity_to_buy(item):
    return item.quantity - get_number_reserved_items_in_preorders(item)


def _add_items_to_basket_or_redirect(request,
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

    # Add item to the basket and create Order if it doesn't exist yet
    quantity = basket_item_form.cleaned_data['quantity']
    order = _create_or_get_preorder(request)

    try:  # Item already in the basket -> change quantity
        item_in_basket = BasketItem.objects.get(item_to_buy=item, order=order)
        item_in_basket.quantity += quantity
        item_in_basket.save()

    except ObjectDoesNotExist:
        BasketItem.objects.create(item_to_buy=item, quantity=quantity,
                                  order=order)
    messages.success(request, "Item added to the basket.")


def _create_or_get_preorder(request):
    if request.user.is_anonymous:
        return _create_or_get_preorder_anonymous_user(
            anonymous_user_with_saved_session(request))
    else:
        return _create_or_get_preorder_user(request.user)


def _create_or_get_preorder_anonymous_user(anon_user):
    try:
        return Order.objects.get(buyer_anon=anon_user, status='preorder')
    except ObjectDoesNotExist:
        return Order.objects.create(buyer_anon=anon_user, status="preorder")


def _create_or_get_preorder_user(user):
    try:
        return Order.objects.get(buyer=user, status='preorder')
    except ObjectDoesNotExist:
        return Order.objects.create(buyer=user, status="preorder")


def _get_preorder_or_none(request):
    try:
        if request.user.is_anonymous:
            return Order.objects.get(
                status='preorder',
                buyer_anon=anonymous_user_with_saved_session(request))
        else:
            return Order.objects.get(status='preorder', buyer=request.user)
    except ObjectDoesNotExist:
        return None
