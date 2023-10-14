import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favourites, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag, User, Subscribe)


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


# ----------------------USER-----------------------------------
# class UserSerializer(serializers.ModelSerializer):
#     """User Serializer."""

#     class Meta:
#         model = User
#         fields = ('email', 'username', 'first_name',
#                   'last_name', 'password')


class PostUserSerializer(serializers.ModelSerializer):
    """User Serializer для POST запросов.

    POST /api/users/ регистрация пользователя
    """

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


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

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()


# -------------------------TAG----------------------------------
class TagSerializer(serializers.ModelSerializer):
    """Tag Serializer.

    Обрабатывает только GET запросы.

    GET /api/tags/ список тэгов
    GET /api/tags/{id}/ получение тэга
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


# ------------------------INGREDIENT-----------------------------
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


# ----------------------RECIPE---------------------------------
class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    """Recipe Subscriptions Serializer для GET запросов.

    Необходимые поля для отображения в подписках.
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


class GetRecipeSerializer(serializers.ModelSerializer):
    """Recipe Serializer для GET запросов.

    GET /api/recipes/ список рецептов
    GET /api/recipes/{id}/ получение рецепта
    """

    tags = TagSerializer(
        many=True)
    author = GetUserSerializer()
    ingredients = IngredientsAmountSerializer(
        many=True,
        source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=False,
        allow_null=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        """Находится ли в избранном."""
        return (
            self.context.get('request').user.is_authenticated
            and Favourites.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Есть ли в списке покупок."""
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists())


class AddIngredientsSerializer(serializers.ModelSerializer):
    """POST запрос для добавления ингридиентов в рецепт.

    Определяем необхолимые поля при создании рецепта.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=True)

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
    ingredients = AddIngredientsSerializer()
    id = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'author')

    def validate_tags(self, tags):
        """Проверка наличия тэга."""
        if not tags:
            raise serializers.ValidationError('Выберите тэг.')

    def validate_ingredients(self, ingredients):
        """Проверка наличия ингридиента."""
        if not ingredients:
            raise serializers.ValidationError('Выберите ингредиент.')

        ingredient_id_list = [item['id'] for item in ingredients]
        if len(ingredient_id_list) != len(set(ingredient_id_list)):
            raise serializers.ValidationError('Уникальны.')

    def validate(self, data):
        """Возвращаем результат валидации."""
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        self.validate_tags(tags)
        self.validate_ingredients(ingredients)

        return data


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
        fields = ('ingredients', 'amount', 'measurement_unit')

    def get_ingredient(self, obj):
        return obj.recipe.ingredients.name

    def get_amount(self, obj):
        return obj.recipe.amount

    def get_measurement_unit(self, obj):
        return obj.recipe.measurement_unit


# -----------------------FAVORITE-------------------------
class FavouritesSerializer(serializers.ModelSerializer):
    """Favourites Serializer."""

    class Meta:
        model = Favourites
        fields = ('recipe', 'user')


# -----------------------SUBSCRITIONS-----------------------
class SubscriptionsSerializer(serializers.ModelSerializer):
    """Subscriptions Serializer.

    Определяем подписки.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscribe.objects.filter(user=self.context['request'].user,
                                         author=obj).exists())

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSubscriptionsSerializer(
            recipes,
            many=True,
            read_only=True)
        return serializer.data


class SubscribeUserSerializer(serializers.ModelSerializer):
    """POST запрос на подписку/отписку на/от авторов."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = SubscriptionsSerializer(
        many=True,
        read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'username')

    def validate(self, obj):
        if (self.context['request'].user == obj):
            raise serializers.ValidationError({'errors': 'Ошибка подписки.'})
        return obj

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscribe.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
