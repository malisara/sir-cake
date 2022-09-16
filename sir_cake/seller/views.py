from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import Item
from .forms import NewItemForm


def new_product(request):
    if request.method == "POST":
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New product successfully saved")
            # TODO redirect
        else:
            messages.error(
                "Error: Unable to save the product. Please try again.")
    else:
        form = NewItemForm()

    return render(request, 'seller/new_product.html', {'form': form})


def item_detail(request, pk):
    try:
        item = Item.objects.get(id=pk)
        item.assign_category_full_name()
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    return render(request, 'seller/item-detail-page.html', {'item': item})
