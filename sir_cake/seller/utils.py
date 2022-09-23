from django.core.paginator import Paginator

from .models import Item


def all_products_context(request):
    # Returns paginated items & responsive url name
    url_name = request.resolver_match.url_name

    # TODO sort results

    items = Item.objects.all().order_by('-id')
    if len(items) == 0:
        return {'items': None,
                'url_name': url_name,
                }

    searched = request.GET.get('searched')
    if searched is not None and searched != "":
        items = items.filter(title__icontains=searched)
    items = pagination(request, items, 15)

    return {
        'items': items,
        'url_name': url_name,
    }


def pagination(request, item_list, number_items_displayed):
    paginator = Paginator(item_list, number_items_displayed)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
