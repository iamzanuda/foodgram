from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .serializers import (FavouritesSerializer,
                          GetRecipeSerializer, PostRecipeSerializer,
                          ShoppingCartSerializer, IngredientSerializer,
                          TagSerializer, SubscriptionsSerializer,
                          SubscribeUserSerializer)
from recipes.models import (Favourites, Ingredient, Recipe,
                            ShoppingCart, Tag, User, Subscribe)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet User."""

    queryset = User.objects.all()
    serializer_class = SubscribeUserSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['GET'])
#            permission_classes=[IsAuthenticated]
    def subscriptions(self, request):
        """Возвращает пользователей,
        на которых подписан текущий пользователь.
        """
        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user))
        serializer = SubscriptionsSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['POST', 'DELETE'])
#            permission_classes=[IsAuthenticated]
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SubscribeUserSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=self.request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscribe, user=self.request.user, author=author)
            subscription.delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet Recipe."""

    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = []

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от типа запроса."""

        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return PostRecipeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Ingredient.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """ViewSet ShoppingList.
    """
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (AllowAny,)


@action(detail=True, methods=['post', 'delete'])
class FavouritesViewSet(viewsets.ModelViewSet):
    """ViewSet Favourites.
    """
    queryset = Favourites.objects.all()
    serializer_class = FavouritesSerializer
    permission_classes = (AllowAny,)
