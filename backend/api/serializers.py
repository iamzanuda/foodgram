import base64

from django.core.files.base import ContentFile
from django.forms import ValidationError
# from django.shortcuts import get_object_or_404
from rest_framework import serializers, status

from recipes.models import (Favourite,
                            Ingredient,
                            IngredientsAmount,
                            Recipe,
                            ShoppingCart,
                            Tag,
                            User,
                            Follow,
                            Favourite,
                            )


class Base64ImageField(serializers.ImageField):
    """Преобразовывает бинарные данные в текстовый формат,
    затем передает получившуюся текстовую строку через JSON,
    а при получении превращает строку обратно в бинарные данные,
    то есть в файл.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    """Регистрация пользователя.

    POST /api/users/ регистрация пользователя
    """

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class UserListSerializer(serializers.ModelSerializer):
    """Список пользователей.

    GET /api/users/ список пользователей
    GET /api/users/{id}/ профиль пользователя
    GET /api/users/me/ текущий пользователь
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return user.following.filter(user=obj).exists()


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Необходимые поля для отображения в 'Мои подписки' и в 'Избранное'."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image',
                  'cooking_time')
        # read_only_fields = ('id', 'name', 'image',
        #                     'cooking_time')

class FollowingSerializer(serializers.ModelSerializer):
    """Для страницы 'Мои подписки'.

    Возвращает пользователей, на которых подписан текущий пользователь
    и дает возможность подписаться.

    В выдачу добавляются рецепты.

    GET /api/users/subscriptions/
    POST /api/users/1/subscribe/
    """

    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count'
                  )
        read_only_fields = ('email',
                            'username',
                            'first_name',
                            'last_name',
                            )

    def validate(self, data):
        """Проверяем подписки."""

        author = self.instance
        user = self.context.get('request').user

        if user.following.filter(following=author).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST,
            )

        if user == author:
            raise ValidationError(
                'Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST,
            )

        return data

    def get_is_subscribed(self, obj):

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user,
                following=obj).exists()
        return False

    def get_recipes(self, obj):

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = BriefRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Tag Serializer.

    Обрабатывает только GET запросы.

    GET /api/tags/ список тэгов
    GET /api/tags/{id}/ получение тэга
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Brief Recipe Serializer для GET запросов.

    Необходимые поля для отображения в подписках и в списке избранного.
    """

    image = Base64ImageField(
        required=False,
        allow_null=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image',
                  'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient Serializer.

    Обрабатывает только GET запросы.

    GET /api/ingredients/ список ингридиентов
    GET /api/ingredients/{id}/ ингридиент
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Ingredient Amount Serializer для GET запросов.

    Сеарилизатор модели посредника для связи ManyToMany между таблицами
    Recipe и Ingreduent.
    """

    id = serializers.IntegerField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Возвращает список рецептов и рецепт по его id.

    Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.

    GET /api/recipes/ список рецептов
    GET /api/recipes/{id}/ получение рецепта
    """

    tags = TagSerializer(
        many=True)
    author = UserListSerializer()
    ingredients = IngredientsAmountSerializer(
        many=True,
        source='recipes_amount')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=False,
        allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        """Находится ли в избранном."""

        return (self.context.get('request').user.is_authenticated
                and Favourite.objects
                .filter(user=self.context['request'].user,
                        recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Находится ли в списке покупок."""

        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects
                .filter(user=self.context['request'].user,
                        recipe=obj).exists())


class AddIngredientsSerializer(serializers.ModelSerializer):
    """Отображаем необходимые поля при POST запросе на создание рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')


class PostRecipeSerializer(serializers.ModelSerializer):
    """Recipe Serializer для POST запросов.

    POST /api/recipes/ создание рецепта
    """

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = AddIngredientsSerializer(
        many=True)
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(
        required=False,
        allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate_tags(self, value):
        """Проверяем наличие тэгов."""

        if not value:
            raise ValidationError('Добавьте тег.')
        return value

    def validate_ingredients(self, value):
        """Проверяем наличие и дублирование ингридиентов."""

        if not value:
            raise ValidationError('Добавьте ингредиент.')

        ingredients = [item['id'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Ингридиенты не должны повторяться.'
            )

        return value

    def add_item(self, ingredients, recipe):
        """Добавляем ингридиенты в рецепт."""

        IngredientsAmount.objects.bulk_create(
            [
                IngredientsAmount(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Создаем рецепт на основе валидированных данных."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)  # Создаем рецепт
        recipe.tags.set(tags)  # Добавляем тэг

        self.add_item(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта на основе валидированных данных."""

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.add_item(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """После создания рецепта, показываем
        пользователю страницу с созданным рецепом.
        """

        return GetRecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class FavouriteSerializer(serializers.ModelSerializer):
    """Серилизатор для избранных рецептов."""

    class Meta:
        fields = (
            'recipe', 'user'
        )
        model = Favourite

    def validate(self, data):
        user = data['user']
        if user.favourites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return BriefRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
