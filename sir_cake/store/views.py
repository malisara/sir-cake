from django.shortcuts import render

from seller.models import Item
from sir_cake.utils import all_products_context


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

    # TODO: POST request- add to basket
    return render(request, 'store/store.html', context)
