from django.urls import reverse
from rest_framework import status
from ..models import PaypalProductModel, Purchase
from user.tests.setup import SetUpAuthUser
from faker import Faker
from dotenv import load_dotenv
import ipdb
import os

load_dotenv()

PRODUCT_ID = os.environ.get('PAYPAL_PRODUCT_ID_TEST')

fake = Faker()


class TestCreateOrder(SetUpAuthUser):
    
    def setUp(self):
        super().setUp()
        self.url = reverse('create_order')
        self.headers = {'Authorization': f'Bearer {self.token}'}


        self.product = PaypalProductModel.objects.create(name="Test1", description="Test1DD", home_url="https://example.com", user=self.user, paypal_id_product=PRODUCT_ID)
        
    def test_create_order_success(self):
        data = {'cart': [{'id': self.product.paypal_id_product, 'value': '10.0'}]}

        response = self.client.post(self.url, headers=self.headers, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("status"), "PAYER_ACTION_REQUIRED")
    
    def test_create_order_empty_cart(self):
        data = {'cart': []}

        response = self.client.post(self.url, headers=self.headers, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Cart': Cart cannot be empty.")

    def test_create_order_unverified_user(self):
        self.user.verified = False
        self.user.save()
        data = {'cart': [{'id': self.product.paypal_id_product, 'value': '10.0'}]}

        response = self.client.post(self.url, headers=self.headers, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("msg"), "User account must be verified to make this action.")

    def test_create_order_invalid_product(self):
        data = {'cart': [{'id': "PROD-INVALID", 'value': '10.0'}]}

        response = self.client.post(self.url, headers=self.headers, data=data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Cart': Product doesn't exist.")

    
    def test_create_order_invalid_value(self):
        data = {'cart': [{'id': self.product.paypal_id_product, 'value': 'INVALID'}]}

        response = self.client.post(self.url, headers=self.headers, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), f"Invalid field 'Cart': Invalid value 'INVALID' for product '{self.product.paypal_id_product}'.")


class TestPurchases(SetUpAuthUser):
    def setUp(self):
        super().setUp()

        self.product = PaypalProductModel.objects.create(name="Test1", description="Test1", home_url="https://example.com", user=self.user, paypal_id_product=PRODUCT_ID)
        self.purchase = Purchase.objects.create(
            user=self.user, product=self.product, price=9.99)
        self.url = reverse('purchases')
        self.headers = {'Authorization': f'Bearer {self.token}'}

        
 
    def test_purchases_ok(self):
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data["results"]['total_pages'], 1)
        self.assertEqual(response.data['results']['user_purchases'][0]['product']['name'], 'Test1')

    def test_purchases_unverified_user(self):
        self.user.verified = False
        self.user.save()

        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("msg"), "User account must be verified to make this action.")


