"""Как должна быть настроена админка

- В интерфейс админ-зоны нужно вывести необходимые поля моделей
  и настроить фильтры:
  вывести все модели с возможностью редактирования и удаление записей;

- для модели пользователей добавить фильтр списка по email
  и имени пользователя;

- для модели рецептов:
  -в списке рецептов вывести название и имя автора рецепта;
  -добавить фильтры по автору, названию рецепта, тегам;
  -на странице рецепта вывести общее число добавлений этого
   рецепта в избранное;

- для модели ингредиентов:
  -в список вывести название ингредиента и единицы измерения;
  -добавить фильтр по названию.
"""

from django.contrib import admin
from .models import (Ingredient, Recipe, Tag, User,
                     IngredientsAmount, ShoppingCart, Favourite, Follow)


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'password')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    list_filter = ('author', 'name', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class IngredientsAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ['name']


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(IngredientsAmount, IngredientsAmountAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(Follow, FollowAdmin)
