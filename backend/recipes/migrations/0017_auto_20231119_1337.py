# Generated by Django 3.2.3 on 2023-11-19 06:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20231112_0221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsamount',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)], verbose_name='Время приготовления в минутах'),
        ),
    ]
