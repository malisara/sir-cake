from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import UserRegistrationForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created")
            return redirect('user_login')
        else:
            messages.error(
                request, 'Registration error, please try again')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})
