from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import statistics
from .decorators import user_is_seller


@user_is_seller
@api_view(['GET'])
def sales_status_ratio_api_view(request):
    return Response(statistics.sales_status_ratio())


@user_is_seller
@api_view(['GET'])
def sold_per_category_api_view(request):
    return Response(statistics.sold_per_category())


@user_is_seller
@api_view(['GET'])
def sales_graph_api_view(request):
    return Response(statistics.sales_graph())


@user_is_seller
@api_view(['GET'])
def user_registration_statistic_api_view(request):
    return Response(statistics.user_registration_last_30_days_statistic())


@user_is_seller
@api_view(['GET'])
def un_registered_users_api_view(request):
    return Response(statistics.un_registered_users())
