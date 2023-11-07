from http import HTTPStatus

from django.test import Client, TestCase


class FoodgramAPITestCase(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_recipes_list_exists(self):
        """Проверка доступности списка задач."""
        response = self.guest_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_list_exists(self):
        """Проверка доступности списка задач."""
        response = self.guest_client.get('/api/users/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
