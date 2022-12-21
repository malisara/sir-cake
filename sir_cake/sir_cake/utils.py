from django.core.paginator import Paginator

from seller.models import Item


def all_products_context(request):
    # Returns paginated items & responsive url name
    url_name = request.resolver_match.url_name
    items = Item.objects.all().order_by('-id')

    # Sorting items in store app
    category = request.GET.get('category')
    if category != "" and category is not None and category != 'ALL':
        items = items.filter(category=category)
        category = Item.SHORT_CATEGORY_TO_NAME[category]
    else:
        category = Item.SHORT_CATEGORY_TO_NAME[Item.Category.ALL]

    if items.count() == 0:
        items = None
    else:
        # Search in seller's view
        searched = request.GET.get('searched')
        if searched is not None and searched != "":
            items = items.filter(title__icontains=searched)
        items = pagination(request, items, 15)

    return {
        'items': items,
        'url_name': url_name,
        'category': category
    }


def pagination(request, item_list, number_items_displayed):
    paginator = Paginator(item_list, number_items_displayed)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
