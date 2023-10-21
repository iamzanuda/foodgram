import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile
# from django.forms import ValidationError
from rest_framework import serializers

from recipes.models import (Favourite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag, User, Follow)


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


class PostUserSerializer(serializers.ModelSerializer):
    """User Serializer для POST запросов.

    POST /api/users/ регистрация пользователя
    """

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True}}


class GetUserSerializer(serializers.ModelSerializer):
    """User Serializer для GET запросов.

    GET /api/users/ список пользователей
    GET /api/users/{id}/ профиль пользователя
    GET /api/users/me/ текущий пользователь
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        extra_kwargs = {
            'username': {'required': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return user.following.filter(user=obj).exists()


# -----------------------FOLLOW-----------------------
class BriefRecipeSerializer(serializers.ModelSerializer):
    """Brief Recipe Serializer для GET запросов.

    Необходимые поля для отображения в подписках и в списке избранного.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image',
                  'cooking_time')
        read_only_fields = ('id', 'name', 'image',
                            'cooking_time')


class FollowPostSerializer(serializers.ModelSerializer):
    """Follow Serializer."""

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        ...

    def to_representation(self, instance):
        return FollowGetSerializer(instance.following,
                                   context=self.context).data


class FollowGetSerializer(serializers.ModelSerializer):
    """Возвращает список пользователей,
    на которых подписан текущий пользователь.

    GET /api/users/subscriptions/
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = BriefRecipeSerializer(
        many=True,
        read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'first_name',
                            'last_name', 'is_subscribed',
                            'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user,
                following=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return []

        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = BriefRecipeSerializer(recipes,
                                           many=True,
                                           read_only=True)
        return serializer.data


# -----------------------TAG-----------------------
class TagSerializer(serializers.ModelSerializer):
    """Tag Serializer.

    Обрабатывает только GET запросы.

    GET /api/tags/ список тэгов
    GET /api/tags/{id}/ получение тэга
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


# -----------------------FAVORITE-------------------------
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


class FavouritesSerializer(serializers.ModelSerializer):
    """Только POST запрос для добавления рецепта в список избранного.

    POST /api/recipes/{id}/favorite/ добавить рецепт в избранное
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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

    id = serializers.ReadOnlyField(
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
    author = GetUserSerializer()
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

    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredient.objects.all())

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
        # попробовать добавить поле author, для сохранения текущего юзера
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        extra_kwargs = {
            'id': {'required': True},
            'ingredients': {'required': True},
            'tags': {'required': True},
            'image': {'required': True},
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True}}

    def validate(self, data):
        """Проверяем что пользователь указал тэг
        и выбрал ингридиент.
        """

        tags = data.get('tags', [])
        ingredients = data.get('ingredients', [])
        print(ingredients)
        if not tags or not ingredients:
            raise serializers.ValidationError(
                'Не указан тэг и/или не выбран ингридиент.')

        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                'Тэги не уникальны.')

        ingredient_ids = {
            ingredient['id'].id if isinstance(ingredient['id'], Ingredient)
            else ingredient['id']
            for ingredient in ingredients}

        if len(ingredient_ids) != len(ingredients):
            raise serializers.ValidationError(
                'Ингридиенты не уникальны.')

        return data

    def create(self, validated_data):
        """Создаем новый экземпляр модели рецепта
        на основе валидированных данных.
        """

        tags = validated_data.pop('tags')
        ingredients = list(validated_data.pop('ingredients'))

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            IngredientsAmount(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id'].id),
                amount=ingredient.get('amount'))
        return recipe

    def update(self, instance, validated_data):
        """Обновляем новый экземпляр модели рецепта
        на основе валидированных данных.
        """

        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)

        for ingredient in ingredients_data:
            IngredientsAmount(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id'].id),
                amount=ingredient.get('amount'))

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


# -----------------------SHOPPING CART-----------------------
class ShoppingCartSerializer(serializers.ModelSerializer):
    """ShoppingList Serializer."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')


class DownloadShoppingCart(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('id', 'ingredients', 'amount', 'measurement_unit')

    def get_ingredient(self, obj):
        return obj.recipe.ingredients.name

    def get_amount(self, obj):
        return obj.recipe.ingredients.amount

    def get_measurement_unit(self, obj):
        return obj.recipe.ingredients.measurement_unit
