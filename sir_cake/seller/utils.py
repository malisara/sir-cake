def total_order_price(shopping_bag):
    total_price = 0
    for item in shopping_bag:
        total_price += item.quantity * item.item_to_buy.price
    return total_price


def active_navbar_context_processor(request):
    context = {}
    if not request.user.is_staff:
        return context

    if 'item' in request.resolver_match.url_name:
        context['url_name'] = 'seller_all_items'
    elif 'order' in request.resolver_match.url_name:
        context['url_name'] = 'seller_orders'
    elif 'overview' in request.resolver_match.url_name:
        context['url_name'] = 'seller_overview'
    else:
        context['url_name'] = None

    return context
