import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter, SearchIngredientFilter
from .pagination import CustomLimitPaginanation
from .permissions import IsUserOrAdmin
from .serializers import (BriefRecipeSerializer, FollowingSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          PostRecipeSerializer, TagSerializer,
                          UserListSerializer)
from recipes.models import (Favourite, Follow, Ingredient, IngredientsAmount,
                            Recipe, ShoppingCart, Tag, User)


class CustomUserViewSet(UserViewSet):
    """Кастомный юзер с определенным набором полей.

    Эндпоинты @action:
        subscriptions
        subscribe
    """

    queryset = User.objects.all()
    pagination_class = CustomLimitPaginanation
    serializer_class = UserListSerializer

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Запрещаем неавторизованному пользователю
        доступ к странице текущего пользователя.
        """

        serializer = UserListSerializer(request.user,
                                        context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя.

        Доступно только авторизованным пользователям.
        """

        user = request.user
        author = get_object_or_404(User, id=kwargs['id'])

        if request.method == 'POST':
            serializer = FollowingSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                subscription = Follow.objects.get(user=user,
                                                  following=author)
            except Follow.DoesNotExist:
                return Response({'errors': 'Подписка не существует.'},
                                status=status.HTTP_400_BAD_REQUEST)

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Возвращает список пользователей,
        на которых подписан текущий пользователь.

        Страница 'Мои подписки'
        """

        user_following_ids_set = set(
            Follow
            .objects
            .filter(user=request.user)
            .values_list('following', flat=True)
        )

        queryset = self.paginate_queryset(
            User.objects.filter(pk__in=user_following_ids_set)
        )

        serializer = FollowingSerializer(
            queryset,
            many=True,
            context={'request': request})

        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получаем список рецептов (api/recipes/)
    и конкретный рецепт (api/recipes/id).

    Эндпоинты @action:
        /download_shopping_cart
        /shopping_cart
        /favorite
    """

    queryset = Recipe.objects.all()
    pagination_class = CustomLimitPaginanation
    permission_classes = (IsUserOrAdmin,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Сохраняем текущего пользователя."""

        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от типа запроса."""

        if self.action in SAFE_METHODS:
            return GetRecipeSerializer
        return PostRecipeSerializer

    def add_or_remove(self, request, model, recipe, message):
        """Общая функция создания/удаления для
        списка избранного и списка покупок.

        Настроена проверка на существование рецепта перед
        созданием и удалением.

        Проверка на наличие рецепта в корзине или в избранном,
        для избежания повторного добавления.
        """

        if request.method == 'POST':
            serializer = BriefRecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)

            if not model.objects.filter(user=request.user,
                                        recipe=recipe).exists():
                model.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

            return Response({'errors': 'Уже в списке.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if not model.objects.filter(user=request.user,
                                        recipe=recipe).exists():
                return Response({'errors': 'Рецепт не существует.'},
                                status=status.HTTP_400_BAD_REQUEST)

            get_object_or_404(model, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': message},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавить рецепт в список избранное.

        Доступно только авторизованным пользователям.
        """

        recipe = get_object_or_404(Recipe, id=pk)

        return self.add_or_remove(
            request,
            Favourite,
            recipe,
            'Рецепт удален из избранного.'
        )

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавить рецепт в список покупок.

        Доступно только авторизованным пользователям.
        """

        recipe = get_object_or_404(Recipe, id=pk)

        return self.add_or_remove(
            request,
            ShoppingCart,
            recipe,
            'Рецепт удален из списка покупок.'
        )

    @action(detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, pk=None):
        """Из рецептов находящихся в списке покупок достаем ингридиенты,
        сумируем их количество если ингридиенты совпадают, записываем
        полученные данные в фаил .txt и отдаем пользователю.
        """

        ingredients_amounts = IngredientsAmount.objects.select_related(
            'recipe', 'ingredient'
        ).filter(recipe__shop_recipe__user=request.user)

        receips_in_cart_ids = set(
            ShoppingCart
            .objects
            .filter(user=request.user)
            .values_list('recipe__id', flat=True)
        )

        dict_of_ingredients = {}

        for item in ingredients_amounts:
            if item.recipe.id not in receips_in_cart_ids:
                continue
            ingredient_name = item.ingredient.name
            measurement_unit = item.ingredient.measurement_unit
            if ingredient_name not in dict_of_ingredients:
                dict_of_ingredients[ingredient_name] = {
                    'amount': 0,
                    'measurement_unit': measurement_unit
                }
            dict_of_ingredients[ingredient_name]['amount'] += item.amount

        output = io.StringIO()
        for key, item in dict_of_ingredients.items():
            output.write(f'{key}: {item["amount"]} {item["measurement_unit"]}')
            output.write('\n')
        output.seek(0)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        response.write(output.getvalue())

        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SearchIngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
