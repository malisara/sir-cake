from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponse)
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.utils import timezone
from django.views import View
from io import BytesIO
from xhtml2pdf import pisa

from .decorators import user_is_seller
from .forms import NewItemForm
from .models import Item, Order
from .utils import total_order_price
from sir_cake.utils import all_products_context, pagination
from store.models import BasketItem
from store.utils import get_items_and_prices_and_order_sum


@user_is_seller
def new_item(request):
    if request.method == "POST":
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New item successfully saved")
            return redirect('all_items')
        else:
            messages.error(
                "Error: Unable to save the item. Please try again.")
    else:
        form = NewItemForm()

    return render(request, 'seller/new_item.html', {'form': form})


@user_is_seller
def item_detail(request, pk):
    try:
        item = Item.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    return render(request, 'seller/item-detail-page.html', {'item': item})


@user_is_seller
def all_items(request):
    context = all_products_context(request)
    return render(request, 'seller/all_items.html', context)


@user_is_seller
def edit_item(request, pk):
    try:
        item = Item.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.method == "POST":
        form = NewItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item is successfully updated')
            return redirect('all_items')
        else:
            messages.error(
                request, 'Error: item was not updated. Please try again')
    else:
        form = NewItemForm(instance=item)

    context = {
        'item': item,
        'form': form}

    return render(request, 'seller/edit-item.html', context)


@user_is_seller
def delete_item(request, pk):
    try:
        item = Item.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.method == "POST":
        item.delete()
        messages.success(request, "Item successfully deleted")
        return redirect('all_items')
    return render(request, 'seller/delete-item.html', {'item': item})


@user_is_seller
def orders(request):
    if request.method == 'POST':
        order_ids = request.POST.getlist('checkbox')
        for order_id in order_ids:
            try:
                order = Order.objects.get(id=int(order_id))
            except (ObjectDoesNotExist, ValueError):
                return HttpResponseBadRequest()

            _mark_order_as_shipped(request, order)
        return redirect('orders')

    orders = Order.objects.exclude(
        status=Order.Status.PREORDER).order_by('-order_date')

    order_status = request.GET.get('status')
    if order_status is None:
        order_status = Order.Status.ALL
    if order_status == Order.Status.UNSENT:
        orders = orders.filter(status=Order.Status.PAID)
    if order_status == Order.Status.SHIPPED:
        orders = orders.filter(status=Order.Status.SHIPPED)

    orders_and_prices = []
    for order in orders:
        sum_price = total_order_price(BasketItem.objects.filter(order=order))
        orders_and_prices.append((order, sum_price))

    context = {'url_name': request.resolver_match.url_name,
               'order_status': order_status,
               'items': pagination(request, orders_and_prices, 30)}

    return render(request, 'seller/orders.html', context)


@user_is_seller
def order_detail(request, pk):
    try:
        order = Order.objects.exclude(status=Order.Status.PREORDER).get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'POST':
        _mark_order_as_shipped(request, order)
        return redirect('order_detail', pk=(pk))

    context = _order_context(order)
    return render(request, 'seller/order-detail.html', context)


def _mark_order_as_shipped(request, order):
    if order.status != Order.Status.SHIPPED:
        order.status = Order.Status.SHIPPED
        order.save()
        messages.success(request, 'Order marked as shipped')


def _order_context(order):
    context = get_items_and_prices_and_order_sum(
        BasketItem.objects.filter(order=order))
    context['order'] = order
    context['anonymous'] = order.buyer is None
    return context


class UserIsSellerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class PdfInvoiceView(UserIsSellerMixin, View):
    def get(self, request, pk, *_, **__):
        try:
            order = Order.objects.get(id=pk)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        context = _order_context(order)
        context['due_date'] = order.order_date + \
            timezone.timedelta(days=settings.INVOICE_DUE_DATE_DAYS)
        pdf = _render_pdf('seller/invoice.html', context, request)
        return HttpResponse(pdf, content_type='application/pdf')


def _render_pdf(template_source, context, request):
    template = get_template(template_source)
    html = template.render(context)
    result = BytesIO()
    status = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not status.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    messages.error(request, 'Could not generate PDF invoice')
    return redirect('orders')
