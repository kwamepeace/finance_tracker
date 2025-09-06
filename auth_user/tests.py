from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import CustomUser, Portfolio, Holdings, Stock
import json

class ViewsTestCase(APITestCase):
    """
    Test suite for the Django views and API endpoints.
    """

    def setUp(self):
        """
        Set up the test data and client for all tests.
        """
        self.user_email = "kwamepeace419@gmail.com"
        self.user_password = "1234567890qwert"
        self.user_username = "kwamepeace"

        # Create a test user for authenticated requests
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            username=self.user_username,
            password=self.user_password,
            date_of_birth='1990-01-01'
        )

        # Get or create the token for authentication
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a test portfolio for the user
        self.portfolio = Portfolio.objects.create(user=self.user, name="My Portfolio")

        # Create a test stock and holding for a known symbol
        self.stock_symbol = "AAPL"
        self.stock = Stock.objects.create(symbol=self.stock_symbol)
        self.holding = Holdings.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            quantity=10,
            purchase_price=150.00
        )
    
    # --- Tests for Auth ViewSet ---
    def test_register_user_success(self):
        """
        Test that a new user can be registered successfully.
        """
        url = reverse('register')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "password2": "password123",
            "date_of_birth": "1995-05-05"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)

    def test_register_user_invalid_data(self):
        """
        Test that registration fails with invalid data (e.g., mismatched passwords).
        """
        url = reverse('register')
        data = {
            "username": "invaliduser",
            "email": "invalid@example.com",
            "password": "password123",
            "password2": "differentpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The serializer returns a specific password error, so we check for it.
        self.assertIn('password', response.data)

    def test_user_login_success(self):
        """
        Test that a user can log in with correct credentials.
        """
        url = reverse('login')
        data = {
            "email": self.user_email,
            "password": self.user_password
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_login_invalid_credentials(self):
        """
        Test that login fails with incorrect credentials.
        """
        url = reverse('login')
        data = {
            "email": self.user_email,
            "password": "wrong_password"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    # --- Tests for Holdings ViewSet ---
    def test_get_holdings_list_authenticated(self):
        """
        Test that an authenticated user can retrieve their holdings list.
        """
        url = reverse('holdings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_new_holding_success(self):
        """
        Test that a user can add a new stock holding to their portfolio.
        """
        url = reverse('holdings-list')
        data = {
            "portfolio_id": self.portfolio.id,
            "symbol": "GOOG",
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
            "portfolio_id": self.portfolio.id,
            "symbol": self.stock_symbol,  # AAPL already exists
            "quantity": 5,
            "purchase_price": 200.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

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

    def test_delete_other_users_holding_failure(self):
        """
        Test that a user cannot delete another user's holding.
        """
        # Create a second user and their portfolio/holding
        other_user = CustomUser.objects.create_user(email="other@example.com", username="other", password="password")
        other_portfolio = Portfolio.objects.create(user=other_user, name="Other Portfolio")
        other_holding = Holdings.objects.create(
            portfolio=other_portfolio,
            stock=self.stock,
            quantity=5,
            purchase_price=10.00
        )

        # Try to delete the other user's holding with our token
        url = reverse('holdings-detail', args=[other_holding.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Tests for Portfolio ViewSet ---
    def test_get_portfolio_data(self):
        """
        Test that the API returns the portfolio data correctly.
        """
        url = reverse('portfolio-my-portfolio')
        response = self.client.get(url)

        # Check that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The API returns a list, so we get the first item
        portfolio_data = response.data[0]
        self.assertEqual(portfolio_data['name'], "My Portfolio")
        self.assertIn('stocks', portfolio_data)
        self.assertEqual(len(portfolio_data['stocks']), 1)
