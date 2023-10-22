import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny  # IsAuthenticated
from rest_framework.response import Response

from .serializers import (BriefRecipeSerializer, FollowGetSerializer,
                          FollowPostSerializer, GetRecipeSerializer,
                          GetUserSerializer, IngredientSerializer,
                          PostRecipeSerializer, PostUserSerializer,
                          TagSerializer)
from recipes.models import (Favourite, Follow, Ingredient, IngredientsAmount,
                            Recipe, ShoppingCart, Tag, User)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet User.

    Эндпоинты @action:
        subscriptions
        subscribe
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от типа запроса."""

        if self.action in ('list', 'retrieve'):
            return GetUserSerializer
        return PostUserSerializer

    @action(detail=False,
            methods=['GET'],
            permission_classes=[AllowAny])  # IsAuthenticated
    def subscriptions(self, request):
        """Возвращает список пользователей,
        на которых подписан текущий пользователь.
        """

        queryset = User.objects.in_bulk(
            Follow
            .objects
            .filter(user=request.user)
            .values_list('following', flat=True))

        serializer = FollowGetSerializer(
            queryset.values(),
            many=True,
            context={'request': request})
        return Response(serializer.data)

    @action(detail=False,
            methods=['POST', 'DELETE'],
            permission_classes=[AllowAny])  # IsAuthenticated
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя.

        Доступно только авторизованным пользователям.
        """

        following_user = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = FollowPostSerializer(
                data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            subscribe, created = Follow.objects.get_or_create(
                user=request.user,
                following=following_user)
            if created:
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            subscription = get_object_or_404(Follow,
                                             user=request.user,
                                             following=following_user)

            subscription.delete()
            return Response({'detail': 'Вы отписались от текущего автора.'},
                            status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получаем список рецептов (api/recipes/)
    и конкретный рецепт (api/recipes/id).

    Эндпоинты @action:
        download_shopping_cartself
        shopping_cart
        favorite
    """

    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Сохраняем текущего пользователя."""

        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от типа запроса."""

        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return PostRecipeSerializer

    @action(detail=False,
            methods=['GET'],
            permission_classes=[AllowAny],  # IsAuthenticated
            url_path='download-shopping-cart')
    def download_shopping_cart(self, request, pk=None):
        """Достаем ингридиент и количество, отдаем пользователю
        фаил в формате txt .
        """

        ingredients_amounts = IngredientsAmount.objects.select_related(
            'recipe', 'ingredient').filter(recipe__author=request.user)

        print(ingredients_amounts)

        list_of_ingredients = []

        for item in ingredients_amounts:
            print(item.recipe)
            for ingredient in item.recipe.ingredients.all():
                print(item.recipe)
                ingredient_name = ingredient.name
                amount = item.amount
                measurement_unit = ingredient.measurement_unit
                list_of_ingredients.append(
                    f'{ingredient_name}: {amount} {measurement_unit}')

        output = io.StringIO()
        print(output)
        for item in list_of_ingredients:
            output.write(item)
            output.write('\n')
        output.seek(0)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'
        response.write(output.getvalue())

        return response

    @action(detail=False,
            methods=['POST', 'DELETE'],
            permission_classes=[AllowAny],  # IsAuthenticated
            url_path='shopping-cart')
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок.
        """

        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = BriefRecipeSerializer(recipe,
                                               data=request.data,
                                               context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user,
                                            recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже есть в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            favourite = get_object_or_404(ShoppingCart,
                                          user=request.user,
                                          recipe=recipe)
            favourite.delete()
            return Response({'detail': 'Рецепт удален из списка.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['POST', 'DELETE'],
            permission_classes=[AllowAny])  # IsAuthenticated
    def favorite(self, request, pk=None):
        """Добавить рецепт в список избранное.

        Доступно только авторизованным пользователям.
        """

        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = BriefRecipeSerializer(recipe,
                                               data=request.data,
                                               context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Favourite.objects.filter(user=request.user,
                                            recipe=recipe).exists():
                Favourite.objects.create(user=request.user,
                                         recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже находится в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            favourite = get_object_or_404(Favourite,
                                          user=request.user,
                                          recipe=recipe)
            favourite.delete()
            return Response({'detail': 'Рецепт удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Ingredient.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


# class ShoppingCartViewSet(viewsets.ModelViewSet):
#     """ViewSet ShoppingList.
#     """
#     queryset = ShoppingCart.objects.all()
#     serializer_class = ShoppingCartSerializer
#     permission_classes = (AllowAny,)


# class FavouritesViewSet(viewsets.ModelViewSet):
#     """ViewSet Favourites.
#     """
#     queryset = Favourites.objects.all()
#     serializer_class = FavouritesSerializer
#     permission_classes = (AllowAny,)


# class FollowViewSet(viewsets.ModelViewSet):
#     """ViewSet Follow.

#     Вьюпоинты:
#         GET /api/users/subscriptions/
#         POST /api/users/{id}/subscribe/
#     """

#     serializer_class = FollowGetSerializer
#     permission_classes = (AllowAny,)
#     # http_method_names = ['get', 'post', 'patch', 'delete']

#     def get_queryset(self):
#         return User.objects.filter(following__user=self.request.user)