import io

from django.http import HttpResponse
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .pagination import CastomLimitPaginanation

from .serializers import (BriefRecipeSerializer,
                          FollowingSerializer,
                          GetRecipeSerializer,
                          UserListSerializer,
                          IngredientSerializer,
                          PostRecipeSerializer,
                          UserCreateSerializer,
                          TagSerializer,
                          FavouriteSerializer,
                          )
from recipes.models import (
                            Follow,
                            Ingredient,
                            IngredientsAmount,
                            Recipe,
                            ShoppingCart,
                            Tag,
                            User,
                            )
from .filters import IngredientFilter, RecipeFilter


class CustomUserViewSet(UserViewSet):
    """ViewSet Custom User.

    Эндпоинты @action:
        subscriptions
        subscribe
    """
    queryset = User.objects.all()
    pagination_class = CastomLimitPaginanation

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от типа запроса."""

        if self.action in ('list', 'retrieve'):
            return UserListSerializer
        return UserCreateSerializer

    @action(detail=False,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя.

        Доступно только авторизованным пользователям.
        """

        following_user = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = FollowingSerializer(
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

    @action(detail=False,
            methods=['GET'],
            )
    def subscriptions(self, request):
        """Возвращает список пользователей,
        на которых подписан текущий пользователь.

        Страница 'Мои подписки'
        """

        # queryset = User.objects.in_bulk(
        #     Follow
        #     .objects
        #     .filter(user=request.user)
        #     .values_list('following', flat=True)
        # )
        queryset = (
            User
            .objects
            .all()
        )
        # page = self.pagination_class.paginate_queryset(queryset, request)
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        page = paginator.paginate_queryset(queryset, request)

        serializer = FollowingSerializer(
            page,
            many=True,
            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

        # queryset = User.objects.filter(following=request.user)
        # print(queryset)

        # serializer = FollowingSerializer(
        #     queryset.values(),
        #     many=True,
        #     context={'request': request})
        # return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получаем список рецептов (api/recipes/)
    и конкретный рецепт (api/recipes/id).

    Эндпоинты @action:
        download_shopping_cartself
        shopping_cart
        favorite
    """

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

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
            permission_classes=[IsAuthenticated],
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
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        response.write(output.getvalue())

        return response

    @action(detail=False,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated],
            url_path='shopping-cart')
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""

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
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить рецепт в список избранное.

        Доступно только авторизованным пользователям.
        """

        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavouriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # filterset_class = IngredientFilter
    pagination_class = None
