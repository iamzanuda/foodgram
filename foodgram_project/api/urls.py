from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavouritesViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')

router.register('recipes', RecipeViewSet, basename='recipes')

router.register('ingredients', IngredientViewSet, basename='ingredients')

router.register('shopping_cart', ShoppingCartViewSet, basename='shopping-cart')

router.register('favourite', FavouritesViewSet, basename='favourite')


urlpatterns = [
    # Можно добавить версию апи(v1)
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
