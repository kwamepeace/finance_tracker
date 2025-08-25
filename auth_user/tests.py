from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from unittest.mock import patch
from .models import CustomUser, Portfolio, Holdings, Stock
from .services import get_live_stock_price
import json

class ViewsTestCase(APITestCase):
    """
    Test suite for the Django views and API endpoints.
    """

    def setUp(self):
        """
        Set up the test data and client for all tests.
        """
        self.user_email = "testuser@example.com"
        self.user_password = "testpassword123"
        self.user_username = "testuser"

        # Create a test user for authenticated requests
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            username=self.user_username,
            password=self.user_password,
            date_of_birth='1990-01-01'
        )

        # Get the token for authentication
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a test portfolio for the user
        self.portfolio = Portfolio.objects.create(user=self.user, name="My Test Portfolio")

        # Create a test stock and holding
        self.stock_symbol = "AAPL"
        self.stock = Stock.objects.create(symbol=self.stock_symbol, name="Apple Inc.")
        self.holding = Holdings.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            quantity=10,
            purchase_price=150.00
        )

    def test_register_user_success(self):
        """
        Test that a new user can be registered successfully.
        """
        url = reverse('auth-register')
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "password2": "newpassword123",
            "date_of_birth": "1995-05-05"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertTrue(CustomUser.objects.filter(email="newuser@example.com").exists())

    def test_login_user_success(self):
        """
        Test that an existing user can log in successfully.
        """
        url = reverse('auth-login')
        data = {
            "email": self.user_email,
            "password": self.user_password
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)

    def test_login_user_failure(self):
        """
        Test that login fails with invalid credentials.
        """
        url = reverse('auth-login')
        data = {
            "email": self.user_email,
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_create_portfolio_success(self):
        """
        Test that a user can create a portfolio successfully.
        """
        # Create a new user without a portfolio to test creation
        new_user = CustomUser.objects.create_user(
            email="anotheruser@example.com",
            username="anotheruser",
            password="password123"
        )
        new_token = Token.objects.get(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + new_token.key)

        url = reverse('portfolio-list')
        data = {"name": "Another User's Portfolio"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Portfolio.objects.filter(user=new_user).exists())

    def test_create_portfolio_failure_already_exists(self):
        """
        Test that a user cannot create a second portfolio.
        """
        url = reverse('portfolio-list')
        data = {"name": "My Second Portfolio"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('auth_user.services.get_live_stock_price', return_value=160.00)
    def test_get_my_portfolio_success(self, mock_get_live_stock_price):
        """
        Test that the user can retrieve their portfolio and live prices are calculated.
        We mock the external API call to ensure the test is fast and reliable.
        """
        url = reverse('portfolio-my-portfolio')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn('name', data)
        self.assertIn('stocks', data)
        self.assertIn('total_portfolio_value', data)
        self.assertEqual(data['name'], "My Test Portfolio")
        
        # Verify that the live price and value are correctly calculated
        stock_data = data['stocks'][0]
        self.assertEqual(stock_data['symbol'], self.stock_symbol)
        self.assertEqual(stock_data['quantity'], 10)
        self.assertEqual(stock_data['current_price'], 160.00)
        self.assertEqual(stock_data['current_value'], 1600.00)
        self.assertEqual(data['total_portfolio_value'], 1600.00)

    def test_add_stock_to_portfolio_success(self):
        """
        Test that a user can add a new stock to their portfolio.
        """
        url = reverse('holdings-list')
        data = {
            "stock_symbol": "GOOG",
            "quantity": 5,
            "purchase_price": 2000.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Holdings.objects.filter(portfolio=self.portfolio, stock__symbol="GOOG").exists())
        self.assertEqual(Holdings.objects.get(stock__symbol="GOOG").quantity, 5)

    def test_add_existing_stock_to_portfolio_failure(self):
        """
        Test that a user cannot add the same stock twice.
        """
        url = reverse('holdings-list')
        data = {
            "stock_symbol": self.stock_symbol,  # AAPL already exists
            "quantity": 5,
            "purchase_price": 200.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_holding_success(self):
        """
        Test that a stock can be deleted from a user's portfolio.
        """
        # Get the ID of the holding to delete
        holding_id = self.holding.id
        url = reverse('holdings-detail', args=[holding_id])
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Holdings.objects.filter(id=holding_id).exists())

