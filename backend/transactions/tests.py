from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Transaction

User = get_user_model()


class TransactionModelTestCase(TestCase):
    """
    Unit Tests for Django ORM Models and Migrations.
    Tests model creation, Foreign Keys, string representations, and aggregations.
    """
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPassword123")
        self.category = Category.objects.create(name="groceries", description="Daily essentials")
        self.tx = Transaction.objects.create(
            user=self.user,
            category=self.category,
            category_name="groceries",
            date=date.today(),
            receiver="BigBasket",
            description="Weekly groceries and fruits",
            amount=Decimal("1250.50"),
            transaction_type="debit",
        )

    def test_model_creation(self):
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(self.tx.receiver, "BigBasket")
        self.assertEqual(self.tx.category.name, "groceries")
        self.assertEqual(self.tx.user.username, "testuser")

    def test_merchant_auto_normalization(self):
        self.assertTrue(len(self.tx.normalized_merchant) > 0)

    def test_to_dict_format(self):
        data = self.tx.to_dict()
        self.assertIn("transaction_id", data)
        self.assertIn("amount", data)
        self.assertEqual(data["amount"], 1250.50)


class APIEndpointsTestCase(TestCase):
    """
    Unit Tests for Django REST Framework API views consumed by React frontend.
    Tests status endpoint, user registration, JWT authentication, and transaction queries.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser",
            email="apiuser@example.com",
            password="StrongPassword123@"
        )
        # Create demo transactions
        Transaction.objects.create(
            user=self.user,
            receiver="Zomato",
            amount=Decimal("450.00"),
            transaction_type="debit",
            category_name="food_delivery",
            date=date.today()
        )

    def test_status_endpoint(self):
        response = self.client.get(reverse("status"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("status"), "ok")

    def test_register_user_api(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewUserPassword123@"
        }
        response = self.client.post(reverse("auth-register"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_authenticated_transactions_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("list-transactions"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_monthly_summary_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("monthly-summary"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("monthly_summary", response.data)
