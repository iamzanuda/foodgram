# Generated by Django 3.2.16 on 2023-10-14 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Время приготовления в минутах'),
        ),
    ]
