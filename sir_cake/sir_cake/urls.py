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
from seller import api_views as api_views
from users import views as user_views
from store import views as store_views


urlpatterns = [
    path('new-item/', seller_views.new_item, name="seller_new_item"),
    path('item/<int:pk>/', seller_views.item_detail, name="seller_item_detail"),
    path('all-items/', seller_views.all_items, name="seller_all_items"),
    path('item/<int:pk>/edit/', seller_views.edit_item,
         name="seller_edit_item"),
    path('item/<int:pk>/delete/', seller_views.delete_item,
         name="seller_delete_item"),
    path('orders/', seller_views.orders, name="seller_orders"),
    path('order/<int:pk>/detail', seller_views.order_detail,
         name="seller_order_detail"),
    path('invoice/<int:pk>/',
         seller_views.PdfInvoiceView.as_view(), name="seller_invoice"),
    path('overview/', seller_views.overview, name="seller_overview"),

    path('js-sales-status-ratio/', api_views.sales_status_ratio_api_view),
    path('js-sold-per-category/', api_views.sold_per_category_api_view),
    path('js-sales-graph/', api_views.sales_graph_api_view),
    path('js-user-registration-statistic/',
         api_views.user_registration_statistic_api_view),
    path('js-un-registered-users/', api_views.un_registered_users_api_view),

    path('register/', user_views.register, name="user_register"),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html'), name="user_login"),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/logout.html'), name="user_logout"),

    path('store/', store_views.store, name="store"),
    path('store/item/<int:pk>/', store_views.store_item_detail,
         name="store_item_detail"),
    path('choose-purchasing-mode/', store_views.choose_purchasing_mode,
         name="store_choose_purchasing_mode"),
    path('shopping-bag/', store_views.shopping_bag, name="store_shopping_bag"),
    path('shipping/', store_views.shipping, name="store_shipping"),
    path('payment/', store_views.payment, name="store_payment"),
    path('successful-purchase/', store_views.successful_purchase,
         name="store_successful_purchase"),
    path('', store_views.landing_page, name="store_landing_page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
