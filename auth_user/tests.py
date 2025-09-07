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

        # Get or create the token for authentication
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a test portfolio for the user
        self.portfolio_name = "My Test Portfolio"
        self.portfolio = Portfolio.objects.create(user=self.user, name=self.portfolio_name)
        
        # Create a stock and a holding for testing purposes
        self.stock_symbol = "AAPL"
        self.stock = Stock.objects.create(symbol=self.stock_symbol)
        self.holding = Holdings.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            quantity=10,
            purchase_price=150.00
        )

    def test_portfolio_list(self):
        """
        Test that the list of portfolios can be retrieved by an authenticated user.
        """
        url = reverse('portfolio-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        


    def test_portfolio_detail_by_name(self):
        """
        Test that a portfolio can be retrieved using its name.
        """
        url = reverse('portfolio-detail', kwargs={'name': self.portfolio_name})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_add_stock_to_portfolio_success(self):
        """
        Test that a new stock can be added to a user's portfolio using the portfolio name.
        """
        url = reverse('holdings-list')
        data = {
            "portfolio_name": self.portfolio_name,
            "symbol": "GOOG",
            "quantity": 5,
            "purchase_price": 2000.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_existing_stock_to_portfolio_failure(self):
        """
        Test that a user cannot add the same stock twice.
        """
        url = reverse('holdings-list')
        data = {
            "portfolio_name": self.portfolio_name,
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
        url = reverse('holdings-detail', kwargs={'pk': holding_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Holdings.objects.filter(id=holding_id).exists())


   