from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """AbstractUser model."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name',
                       'last_name', 'password')

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Адрес электронной почты',)
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        validators=[validate_username],
        verbose_name='Уникальный юзернейм',)
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',)
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',)
    password = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Пароль',)

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
        max_length=200,
        verbose_name='Название тэга')
    color = models.CharField(
        max_length=7,
        choices=TAG_COLOR_CODE,
        verbose_name='Цветовой код')
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг')

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
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    """Recipe model."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsAmount',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Имя автора')
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Изображение блюда')
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта')
    text = models.TextField(
        max_length=500,
        verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(240),
        ),
        verbose_name='Время приготовления в минутах')
    # pub_date = models.DateTimeField(
    #     auto_now_add=True,
    #     verbose_name='Дата публикации',)

    # class Meta:
    #     ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):
    """Модель посредник для связи моделей Recipe и Ingredient."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_amount',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Ингредиенты')
    amount = models.PositiveIntegerField(
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(1000),
        ),
        verbose_name='Количество',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}: {self.amount}'


class ShoppingCart(models.Model):
    """ShoppingCart model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='shop_user',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_recipe',
        verbose_name='Рецепт')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favourite(models.Model):
    """Favourites model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='favourites',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Рецепт')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписан')

    def __str__(self):
        return f'{self.user.username} - {self.following.username}'
