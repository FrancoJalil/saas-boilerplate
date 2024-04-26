from rest_framework.test import APITestCase
from faker import Faker
from django.urls import reverse
from rest_framework import status
from ..models import CustomUser
faker = Faker()

class SetUpAuthUser(APITestCase):
    def setUp(self):
        self.login_url = reverse("auth_credentials")
        self.email = 'francocraftero78@gmail.com'
        self.user = CustomUser.objects.create_superuser(
            first_name="Developer",
            last_name="Developer",
            email=self.email,
            password="Cocoro123",
            verified=True,
        )

        # login
        response = self.client.post(
            self.login_url,
            {'email': self.email,
             'password': 'Cocoro123'},
            format='json'
        )

        self.token = response.data.get("access")
        self.refresh_token = response.data.get("refresh")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

