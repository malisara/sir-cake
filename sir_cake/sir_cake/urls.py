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
from store import views as store_views


urlpatterns = [
    path('new-item/', seller_views.new_item, name="new_item"),
    path('item/<int:pk>/', seller_views.item_detail, name="item_detail"),
    path('all-items/', seller_views.all_items, name="all_items"),
    path('item/<int:pk>/edit/', seller_views.edit_item, name="edit_item"),
    path('item/<int:pk>/delete/', seller_views.delete_item, name="delete_item"),
    path('orders/', seller_views.orders, name="orders"),
    path('order/<int:pk>/detail', seller_views.order_detail,
         name="order_detail"),
    path('invoice/<int:pk>/',
         seller_views.PdfInvoiceView.as_view(), name="invoice"),
    path('overview/', seller_views.overview, name="overview"),

    path('js-sales-status-ratio/', seller_views.sales_status_ratio_js),
    path('js-sold_per_category/', seller_views.sold_per_category),
    path('js-sales-graph/', seller_views.sales_graph_js),
    path('js-user-registration-statistic/',
         seller_views.user_registration_statistic_js),
    path('js-un-regstred-users/', seller_views.un_registred_users_js),

    path('register/', user_views.register, name="register"),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/logout.html'), name="logout"),

    path('store/', store_views.store, name="store"),
    path('store/item/<int:pk>/', store_views.store_item_detail,
         name="store_item_detail"),
    path('choose-purchasing-mode/', store_views.choose_purchasing_mode,
         name="choose_purchasing_mode"),
    path('shopping-bag/', store_views.shopping_bag, name="shopping_bag"),
    path('shipping/', store_views.shipping, name="shipping"),
    path('payment/', store_views.payment, name="payment"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
