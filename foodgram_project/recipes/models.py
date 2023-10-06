# from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model
# from .validators import validate_username
User = get_user_model()

# class User(AbstractUser):
    # """Пользователи.
    # """# 
    # email = models.EmailField(
        # max_length=254,
        # blank=False,
        # unique=True,
        # verbose_name='Адрес электронной почты')
    # username = models.CharField(
        # max_length=150,
        # blank=False,
        # unique=True,
        # validators=[validate_username],
        # verbose_name='Уникальный юзернейм')
    # first_name = models.CharField(
        # max_length=150,
        # blank=False,
        # verbose_name='Имя')
    # last_name = models.CharField(
        # max_length=150,
        # blank=False,
        # verbose_name='Фамилия')
    # password = models.CharField(
        # max_length=150,
        # blank=False,
        # verbose_name='Пароль')

    # def __str__(self):
        # return self.username


class Tags(models.Model):
    """Тег.
    """
    GREEN = '#03c03c'
    RED = '#ff6347'
    BLUE = '#120a8f'
    TAG_COLOR_CODE = [
        (GREEN, 'Завтрак'),
        (RED, 'Обед'),
        (BLUE, 'Ужин'),
    ]
    name = models.CharField(
        max_length=16,
        blank=False,
        unique=True,
        verbose_name='Название тэга')
    color = models.CharField(
        max_length=16,
        blank=False,
        unique=True,
        choices=TAG_COLOR_CODE,
        verbose_name='Цветовой код')
    slug = models.SlugField(
        max_length=50,
        blank=False,
        unique=True,
        verbose_name='Слаг тэга')

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Ингридиенты.
    """
    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название ингридиента')
    measurement_unit = models.CharField(
        max_length=25,
        blank=False,
        verbose_name='Единицы измерения')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт.
    """
    ingredient = models.ManyToManyField(
        Ingredients,
        blank=False,
        through='RecipeIngredients',
        verbose_name='Ингредиенты')
    tags = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        blank=False,
        related_name='recipes_tags',
        verbose_name='Тэг')
    image = models.ImageField(
        upload_to='images/',
        blank=False,
        verbose_name='Изображение блюда')
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название рецепта')
    text = models.TextField(
        max_length=500,
        blank=False,
        verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        blank=False,
        verbose_name='Время приготовления в минутах')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='recipes_author',
        verbose_name='Имя автора')

    def __str__(self):
        return self.author


class ShoppingCart(models.Model):
    """Список покупок.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts_recipe',
        verbose_name='Рецепт')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='shoppingcarts_user',
        verbose_name='Пользователь')

    def __str__(self):
        return self.recipe


class Favourites(models.Model):
    """Избранное.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites_recipe',
        verbose_name='Рецепт')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='favourites_user',
        verbose_name='Пользователь')

    def __str__(self):
        return self.user


class Subscriptions(models.Model):
    """Подписки.
    """
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты')
    username = models.CharField(
        max_length=150,
        unique=True,
        # validators=[validate_username],
        verbose_name='Уникальный юзернейм')
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия')
    is_subscribed = models.BooleanField(
        verbose_name='Подписан ли текущий пользователь на этого')
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт')
    recipes_count = models.IntegerField(
        verbose_name='Общее количество рецептов пользователя')

    def __str__(self):
        return self.username


class RecipeIngredients(models.Model):
    """Модель посредник для моделей Recipe и Ingredients.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Ингредиенты')
    amount = models.IntegerField(
        blank=False,
        verbose_name='Количество')

    def __str__(self):
        return self.recipe
