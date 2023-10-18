from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet, UserViewSet)

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
# router.register('users/subscriptions', FollowViewSet, basename='users-subscriptions')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register('shopping_cart', ShoppingCartViewSet, basename='shopping-cart')
# router.register(r'recipes/(?P<post_id>\d+)/favorite',
#                FavouritesViewSet, basename='recipes-favourite')


urlpatterns = [
    # Можно добавить версию апи(v1)
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
