from django.core.paginator import Paginator


def pagination(request, item_list, number_items_displayed):
    paginator = Paginator(item_list, number_items_displayed)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
