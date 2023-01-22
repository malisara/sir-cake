from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, Sum
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect

from users.models import AnonymousUser, ShippingAddress
from seller.models import Item, Order
from sir_cake.utils import pagination
from store.models import BasketItem
from users.forms import (AnonymousUserUpdateNamesForm,
                         ShippingAddressForm,
                         UserUpdateNamesForm)
from .forms import BasketItemForm, PaymentForm
from .utils import (anonymous_user_without_session,
                    anonymous_user_with_saved_session,
                    get_basket_expire_date,
                    get_items_and_prices_and_order_sum,
                    get_number_reserved_items_in_preorders,
                    get_preorder_or_none)


def store(request):
    form = BasketItemForm(1)
    context = _available_items_and_category_context(request)
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


def _available_items_and_category_context(request):
    # Only items with inventory > 0 and inventory > all users' reservations
    # are returned

    total_quantity_basket_items = BasketItem.objects.filter(
        item_to_buy_id=OuterRef('pk')).values(
            'item_to_buy_id').annotate(total=Sum('quantity')).values('total')

    items_not_in_basket = Item.objects.filter(quantity__gte=0).exclude(
        id__in=BasketItem.objects.values_list('item_to_buy', flat=True))

    items_in_basket_enough_quantity = Item.objects.filter(
        quantity__gt=Subquery(total_quantity_basket_items))

    items = items_in_basket_enough_quantity | items_not_in_basket

    category = request.GET.get('category')
    if category in Item.SHORT_CATEGORY_TO_NAME \
            and category != Item.Category.ALL:
        items = items.filter(category=category)
        category = Item.SHORT_CATEGORY_TO_NAME[category]
    else:
        category = Item.SHORT_CATEGORY_TO_NAME[Item.Category.ALL]

    if items.count() == 0:
        items = None
    else:
        items = items.order_by('-id')
        searched = request.GET.get('searched')
        if searched is not None and searched != "":
            items = items.filter(title__icontains=searched)
        items = pagination(request, items, 30)

    return {'items': items, 'category': category}


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
    return render(request, 'store/choose-purchasing-mode.html')


def shopping_bag(request):
    if anonymous_user_without_session(request):
        return redirect('store_choose_purchasing_mode')

    context = {'step': 1}
    preorder = get_preorder_or_none(request)

    if preorder is None:
        # Shopping bag is empty.
        return render(request, 'store/shopping-bag.html', context)

    if request.method == "POST":
        if "action" not in request.POST:
            return HttpResponseBadRequest()
        if request.POST['action'] not in ["pay", "cancel"] and \
                not request.POST['action'].startswith("delete_"):
            return HttpResponseBadRequest()

    basket_items = BasketItem.objects.filter(order=preorder)

    if request.method == "POST" and request.POST['action'].startswith("delete"):
        # Single item is deleted.
        try:
            delete_pk = int(request.POST.get('action').split('_')[1])
        except ValueError:
            return HttpResponseBadRequest()
        BasketItem.objects.get(id=delete_pk).delete()

        if basket_items.count() != 0:
            messages.success(request, "Item deleted")
        else:
            # Delete order if there are no itemss
            preorder.delete()
            messages.success(
                request, "Your shopping bag is deleted")
            return redirect('store')

    if request.method == "POST" and request.POST['action'] == "cancel":
        # Whole basket is deleted.
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
            if not form.is_valid():
                return redirect('store')
            form.save()
        return redirect('store_shipping')

    context['items_and_forms'] = list(zip(basket_items, forms))
    context['expire_date'] = get_basket_expire_date(
        preorder).strftime("%Y-%m-%d %H:%M:%S")
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
        return 'store_choose_purchasing_mode'

    if not basket_item_form.is_valid():
        error_string = _set_error_message_from_form_errors(
            basket_item_form.errors.as_data().get('quantity', []), request)
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
        return Order.objects.get(buyer_anon=anon_user,
                                 status=Order.Status.PREORDER)
    except ObjectDoesNotExist:
        return Order.objects.create(buyer_anon=anon_user,
                                    status=Order.Status.PREORDER)


def _create_or_get_preorder_user(user):
    try:
        return Order.objects.get(buyer=user, status=Order.Status.PREORDER)
    except ObjectDoesNotExist:
        return Order.objects.create(buyer=user, status=Order.Status.PREORDER)


def shipping(request):
    if anonymous_user_without_session(request):
        return redirect('store_choose_purchasing_mode')

    preorder = get_preorder_or_none(request)
    context = _context_my_bag_total(preorder)
    if context is None:
        return render(request, 'store/shipping.html', {'no_items': True})

    context['step'] = 2
    address_instance = _get_user_address_instance_or_none(request)
    shipping_address_form = _create_shipping_address_form(
        request, address_instance)
    name_form = _create_name_form(request)

    context['name_form'] = name_form
    context['shipping_address_form'] = shipping_address_form

    if request.method == 'POST':
        valid_form_address = _save_address_data(
            request, shipping_address_form,
            first_time_saving=address_instance is None)
        valid_form_name = _save_name_data(request, name_form)
        if valid_form_address and valid_form_name:
            return redirect('store_payment')

    context['expire_date'] = get_basket_expire_date(
        preorder).strftime("%Y-%m-%d %H:%M:%S")
    return render(request, 'store/shipping.html', context)


def _get_user_address_instance_or_none(request):
    # Address instance is None before user makes the first successful payment
    if request.user.is_anonymous:
        try:
            return ShippingAddress.objects.get(
                user_anon=anonymous_user_with_saved_session(request))
        except ObjectDoesNotExist:
            return None
    try:
        return ShippingAddress.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return None


def _create_shipping_address_form(request, address_instance):
    if request.method == 'POST':
        if address_instance is None:
            return ShippingAddressForm(request.POST)
        return ShippingAddressForm(request.POST, instance=address_instance)

    else:
        if address_instance is None:
            return ShippingAddressForm()
        return ShippingAddressForm(instance=address_instance)


def _create_name_form(request):
    if request.method == 'POST':
        if request.user.is_anonymous:
            user = anonymous_user_with_saved_session(request)
            return AnonymousUserUpdateNamesForm(request.POST, instance=user)
        return UserUpdateNamesForm(request.POST, instance=request.user)
    else:
        if request.user.is_anonymous:
            user = anonymous_user_with_saved_session(request)
            return AnonymousUserUpdateNamesForm(instance=user)
        return UserUpdateNamesForm(instance=request.user)


def _save_address_data(request, address_form, first_time_saving):
    if not address_form.is_valid():
        messages.error(request, "Invalid form data.")
        return False

    if first_time_saving:
        shipping_data = address_form.save(commit=False)
        if request.user.is_anonymous:
            shipping_data.user_anon = anonymous_user_with_saved_session(
                request)
        else:
            shipping_data.user = request.user
        shipping_data.save()
    else:
        address_form.save()
    return True


def _save_name_data(request, name_form):
    if not name_form.is_valid():
        messages.error(request, "Invalid form data.")
        return False
    name_form.save()
    return True


def payment(request):
    # Dummy view -> doesn't handle real payments
    if anonymous_user_without_session(request):
        return redirect('store_choose_purchasing_mode')

    preorder = get_preorder_or_none(request)
    if request.method == "POST":
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            preorder.status = Order.Status.PAID
            preorder.save()
            basket_items = BasketItem.objects.filter(order=preorder)
            for item in basket_items:  # Decrease the inventory
                item.item_to_buy.quantity -= item.quantity
                item.item_to_buy.save()
            return redirect('store_successful_purchase')
        else:
            errors_cvv = payment_form.errors.as_data().get('cvv', [])
            errors_credit_card = payment_form.errors.as_data().get(
                'credit_card', [])
            _set_error_message_from_form_errors(
                errors_cvv + errors_credit_card, request)
    else:
        payment_form = PaymentForm()

    context = _context_my_bag_total(preorder)
    if context is None:
        return render(request, 'store/payment.html', {'no_items': True})

    if _shipping_data_is_missing(request):
        messages.error(request, 'Please, enter shipping data')
        return redirect('store_shipping')

    context['step'] = 3
    context['form'] = payment_form
    context['expire_date'] = get_basket_expire_date(
        preorder).strftime("%Y-%m-%d %H:%M:%S")
    return render(request, 'store/payment.html', context)


def _context_my_bag_total(preorder):
    if preorder is None:
        return None

    shopping_bag = BasketItem.objects.filter(order=preorder).order_by('id')
    return get_items_and_prices_and_order_sum(shopping_bag)


def _set_error_message_from_form_errors(errors, request):
    error_string = ''
    for error in errors:
        error_string += " ".join(error.messages) + " "
    messages.error(request, error_string)
    return error_string


def _shipping_data_is_missing(request):
    if request.user.is_anonymous:
        user = anonymous_user_with_saved_session(request)
        return ShippingAddress.objects.filter(user_anon=user).count() == 0
    else:
        return ShippingAddress.objects.filter(user=request.user).count() == 0


def landing_page(request):
    return render(request, 'store/landing-page.html')


def successful_purchase(request):
    return render(request, 'store/successful_purchase.html')
