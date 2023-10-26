from django.contrib import admin

from .models import (Favourite,
                     Follow,
                     Ingredient,
                     IngredientsAmount,
                     Recipe,
                     ShoppingCart,
                     Tag,
                     User,
                     )


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
