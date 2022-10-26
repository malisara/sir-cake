from django.shortcuts import render, redirect

from seller.models import Item
from sir_cake.utils import all_products_context
from .models import AnonymousUser
from .utils import add_one_item_to_basket, anonymous_user_without_session


def store(request):
    if request.method == "POST":
        redirect_or_none = add_one_item_to_basket(request)
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
