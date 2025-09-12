import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Order, OrderUpdate

class ShopViewsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        # Create test order for user
        self.order = Order.objects.create(
            items_json=json.dumps({
                "item1": [2, "Product 1", 100],
                "item2": [1, "Product 2", 200]
            }),
            amount=400,
            name="Test User",
            email=self.user.email,
            address="123 Test St",
            city="Test City",
            state="Test State",
            zip_code="12345",
            phone="1234567890"
        )
        self.order_update = OrderUpdate.objects.create(
            order_id=self.order.order_id,
            update_desc="Order placed",
        )

    def test_my_orders_view(self):
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Orders")
        self.assertContains(response, self.user.email)
        self.assertContains(response, f"Order #{self.order.order_id}")

    def test_initiate_payment_view_valid(self):
        items_json = json.dumps({
            "item1": [2, "Product 1", 100],
            "item2": [1, "Product 2", 200]
        })
        post_data = {
            'itemsJson': items_json,
            'name': 'Test User',
            'email': self.user.email,
            'address1': '123 Test St',
            'address2': '',
            'city': 'Test City',
            'state': 'Test State',
            'zip_code': '12345',
            'phone': '1234567890',
        }
        response = self.client.post(reverse('pay'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "razorpay_key")

    def test_initiate_payment_view_invalid_amount(self):
        items_json = json.dumps({
            "item1": [0, "Product 1", 100],  # zero quantity
        })
        post_data = {
            'itemsJson': items_json,
            'name': 'Test User',
            'email': self.user.email,
            'address1': '123 Test St',
            'address2': '',
            'city': 'Test City',
            'state': 'Test State',
            'zip_code': '12345',
            'phone': '1234567890',
        }
        response = self.client.post(reverse('pay'), post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Cart is empty or invalid amount", response.content)

    def test_my_orders_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
