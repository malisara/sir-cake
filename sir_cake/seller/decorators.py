from functools import wraps

from django.core.exceptions import PermissionDenied


def user_is_seller(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_staff:
            return function(request, *args, **kwargs)
        raise PermissionDenied()
    return wrap
