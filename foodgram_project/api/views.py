from rest_framework import viewsets
from .serializers import (FavouritesSerializer, IngredientsSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionsSerializer, TagsSerializer,
                          RecipeIngredientsSerializer, UserSerializer)
from recipes.models import (Favourites, Ingredients, Recipe, ShoppingCart,
                            Subscriptions, Tags, RecipeIngredients, User)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet User.

    Пагинация
    https://practicum.yandex.ru/trainer/backend-developer/lesson/2e8b7f0e-6b3b-40d1-8690-eec311ad588e/task/78a72e9e-b23f-412a-a2fd-be546432ca7f/?searchedText=LimitOffsetPagination
    Авторизация
    https://practicum.yandex.ru/trainer/backend-developer/lesson/9335cf18-a9a5-4b69-9bb7-dad742ff4c9f/task/142ad06e-3cf1-4cac-96fc-ad2f46f8d7d7/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Tag.
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet Recipe.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    """ViewSet Ingredient.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """ViewSet ShoppingList.
    """
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class FavouritesViewSet(viewsets.ModelViewSet):
    """ViewSet Favourites.
    """
    queryset = Favourites.objects.all()
    serializer_class = FavouritesSerializer


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """ViewSet Subscriptions.
    """
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionsSerializer


class RecipeIngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet RecipeIngredients.
    """
    queryset = RecipeIngredients.objects.all()
    serializer_class = RecipeIngredientsSerializer
