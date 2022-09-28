from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render

from .forms import NewItemForm
from .models import Item
from .utils import all_products_context


def new_item(request):
    if request.method == "POST":
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New item successfully saved")
            # TODO redirect
        else:
            messages.error(
                "Error: Unable to save the item. Please try again.")
    else:
        form = NewItemForm()

    return render(request, 'seller/new_item.html', {'form': form})


def item_detail(request, pk):
    try:
        item = Item.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    return render(request, 'seller/item-detail-page.html', {'item': item})


def all_items(request):
    context = all_products_context(request)
    return render(request, 'seller/all_items.html', context)
