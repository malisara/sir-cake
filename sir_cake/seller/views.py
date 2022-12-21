from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render

from .decorators import user_is_seller
from .forms import NewItemForm
from .models import Item
from sir_cake.utils import all_products_context


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
