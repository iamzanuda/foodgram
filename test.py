from django.contrib.auth.models import AbstractUser

from .validators import validate_username

class User(AbstractUser):
    """Пользователи.
    """
    email = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,
        verbose_name='Адрес электронной почты')
    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
        validators=[validate_username],
        verbose_name='Уникальный юзернейм')
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия')
    password = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Пароль')

    def __str__(self):
        return self.username