from django.shortcuts import render, redirect

from seller.models import Item
from sir_cake.utils import all_products_context
from .models import AnonymousUser
from .utils import add_one_item_basket


def store(request):
    context = all_products_context(request)
    context['all_categories'] = Item.CATEGORIES_CHOICES

    if request.method == "GET":
        category_short = request.GET.get('category')
        if category_short is not None:
            category = Item.SHORT_CATEGORY_TO_NAME[category_short]
            context['category'] = category
        else:
            context['category'] = 'All sweets'
    else:
        redirect_or_none = add_one_item_basket(request, context)
        if redirect_or_none is not None:
            return redirect(redirect_or_none)
    return render(request, 'store/store.html', context)


def continue_purchase(request):  # choose if you'll continue with/-out login
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.create()
            AnonymousUser.objects.create(
                session_id=request.session.session_key)
        return redirect('store')
    return render(request, 'store/continue-purchase.html')
