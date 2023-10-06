from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavouritesViewSet, IngredientsViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscriptionsViewSet, TagsViewSet,
                    UserViewSet)

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('shopping_cart', ShoppingCartViewSet, basename='shopping_cart')
router.register('favourite', FavouritesViewSet, basename='favourite')
router.register('subscriptions', SubscriptionsViewSet,
                basename='subscriptions')
router.register('subscriptions', SubscriptionsViewSet,
                basename='subscriptions')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
