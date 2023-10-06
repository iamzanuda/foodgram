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
from .models import Ingredients, Recipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    list_filter = ('author', 'name', 'tags')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ['name']


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipe, RecipeAdmin)
