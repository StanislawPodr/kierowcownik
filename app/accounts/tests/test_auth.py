from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.me_url = reverse('auth-me')
        self.user_data = {
            'username': 'janek',
            'password': 'haslo12345',
            'password_confirm': 'haslo12345',
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'janek')
        self.assertTrue(User.objects.filter(username='janek').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='janek', password='haslo12345')

        response = self.client.post(self.register_url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_password_mismatch(self):
        data = {**self.user_data, 'password_confirm': 'innehaslo1'}
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_login_success(self):
        User.objects.create_user(username='janek', password='haslo12345')

        response = self.client.post(
            self.login_url,
            {'username': 'janek', 'password': 'haslo12345'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        user = User.objects.create_user(username='janek', password='haslo12345')
        login_response = self.client.post(
            self.login_url,
            {'username': 'janek', 'password': 'haslo12345'},
            format='json',
        )

        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['username'], 'janek')
