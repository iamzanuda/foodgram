from django.http import HttpResponse
from rest_framework.permissions import SAFE_METHODS


def IsAdminOrReadOnly(view_func):
    """Даем доступ только админу."""

    def wrapper(request, *args, **kwargs):
        if request.method in SAFE_METHODS or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse(
                'Действие доступно только администратору.', status=403)
    return wrapper


def IsAuthorOrReadOnly(view_func):
    """Даем доступ только автору."""

    def wrapper(request, *args, **kwargs):
        obj = kwargs.get('obj')
        if request.method in SAFE_METHODS or obj.author == request.user:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse(
                'Действие доступно только автору поста.', status=403)
    return wrapper
