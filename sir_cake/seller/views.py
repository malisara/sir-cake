from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render

from .forms import NewItemForm


def new_product(request):
    if request.method == "POST":
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New product successfully saved")
        else:
            messages.error(
                "Error: Unable to save the product. Please try again.")
    else:
        form = NewItemForm()

    return render(request, 'seller/new_product.html', {'form': form})
