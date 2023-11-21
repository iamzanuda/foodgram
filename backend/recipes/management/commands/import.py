import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Импорт данных из csv файла.'

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            default='ingredients.csv',
                            nargs='?',
                            type=str)

    def handle(self, *args, **options):
        filename = options['filename']
        filepath = os.path.join(DATA_ROOT, filename)

        try:
            ingredients_list = []

            with open(filepath, 'r', encoding='utf-8') as file:
                data = csv.reader(file)
                next(data)

                for row in data:
                    name, measurement_unit = row
                    ingredient = Ingredient(
                        name=name,
                        measurement_unit=measurement_unit)
                    ingredients_list.append(ingredient)

            with transaction.atomic():
                Ingredient.objects.bulk_create(ingredients_list)

            self.stdout.write(
                self.style.SUCCESS(f'Данные из {filename} импортированны.'))

        except FileNotFoundError:
            self.stderr.write('Файл csv не найден')
