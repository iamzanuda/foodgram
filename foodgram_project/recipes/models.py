from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

from .validators import validate_username


class User(AbstractUser):
    """User model."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name',
                       'last_name', 'password']

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты')
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username],
        verbose_name='Уникальный юзернейм')
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия')
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль')

    def __str__(self):
        return self.username


class Tag(models.Model):
    """Tag model."""

    GREEN = '#03c03c'
    RED = '#ff6347'
    BLUE = '#120a8f'
    TAG_COLOR_CODE = [
        (GREEN, 'Зеленый'),
        (RED, 'Красный'),
        (BLUE, 'Синий'),
    ]

    name = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Название тэга')
    color = models.CharField(
        max_length=16,
        unique=True,
        choices=TAG_COLOR_CODE,
        verbose_name='Цветовой код')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг тэга')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Recipe model."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsAmount',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг')
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Изображение блюда')
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта')
    text = models.TextField(
        max_length=500,
        verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Время приготовления в минутах')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Имя автора')

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):
    """Модель посредник для связи моделей Recipe и Ingredient."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт')
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиенты')
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество')

    def __str__(self):
        return f'{self.recipe} - {self.ingredients}: {self.amount}'


class ShoppingCart(models.Model):
    """ShoppingCart model."""

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
        return f'{self.user.username} - {self.recipe.name}'


class Favourites(models.Model):
    """Favourites model."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites_user',
        verbose_name='Рецепт')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='favourites_user',
        verbose_name='Пользователь')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribes_user',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribes_author',
        verbose_name='Подписка'
    )

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
