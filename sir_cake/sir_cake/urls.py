"""sir_cake URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from seller import views as seller_views
from users import views as user_views


urlpatterns = [
    path('new-item/', seller_views.new_item, name="new_item"),
    path('item/<int:pk>/', seller_views.item_detail, name="item_detail"),
    path('all-items/', seller_views.all_items, name="all_items"),
    path('item/<int:pk>/edit/', seller_views.edit_item, name="edit_item"),
    path('item/<int:pk>/delete/', seller_views.delete_item, name="delete_item"),

    path('register/', user_views.register, name="register"),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
