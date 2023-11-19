# Generated by Django 3.2.3 on 2023-11-19 14:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_auto_20231119_1715'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',)},
        ),
        migrations.AddField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=1, verbose_name='Дата публикации'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ingredientsamount',
            name='amount',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(240)], verbose_name='Время приготовления в минутах'),
        ),
    ]