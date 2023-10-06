import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favourites, Ingredients, Recipe, ShoppingCart,
                            Subscriptions, Tags, RecipeIngredients, User)


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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""
    class Meta:
        model = Ingredients
        fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('ingredient', 'tags', 'image', 'name', 'text',
                  'cooking_time', 'author')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели ShoppingList."""
    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')


class FavouritesSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favourites."""
    class Meta:
        model = Favourites
        fields = ('recipe', 'user')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subscriptions."""
    class Meta:
        model = Subscriptions
        fields = ('email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    class Meta:
        model = RecipeIngredients
        fields = ('recipe', 'ingredient', 'amount')
