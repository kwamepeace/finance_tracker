This document provides a comprehensive overview of the Stock Portfolio Tracker, a secure, web-based application built with Django and Django REST Framework.

## 1. Project Overview
The application is designed to allow authenticated users to manage a personal stock portfolio. Upon registration, a single portfolio is automatically created for each user. The application handles the creation, retrieval, updating, and deletion of stock holdings, while also automatically calculating the total value of the portfolio. The project uses token-based authentication to secure user data.

## 2. API Endpoints
The API is built using Django REST Framework's ViewSets. All endpoints, except for registration and login, require an authentication token.

User Authentication
Register a new user

Endpoint: /api/auth/register/

Method: POST

Request Body (JSON):

{
  "email": "user@example.com",
  "password": "yourpassword",
  "password2": "yourpassword",
  "username": "unique_username",
  "date_of_birth": "1990-01-01"
}

Success Response (201 Created):

{
  "token": "a1b2c3d4e5f6...",
  "user_id": 1
}

Log in an existing user

Endpoint: /api/auth/login/

Method: POST

Request Body (JSON):

{
  "email": "user@example.com",
  "password": "yourpassword"
}

Success Response (200 OK):

{
  "token": "a1b2c3d4e5f6..."
}

Portfolio Management
Authentication for these endpoints requires adding Authorization: Token <your_token> to the request headers.

Retrieve the user's portfolio

Endpoint: /api/portfolio/my-portfolio/

Method: GET

Description: Retrieves the authenticated user's portfolio, including all stock holdings and the total portfolio value.

Success Response (200 OK):

{
  "id": 1,
  "name": "User's Portfolio",
  "user": 1,
  "stocks": [
    {
      "id": 1,
      "symbol": "GOOG",
      "quantity": 5,
      "purchase_price": "100.00",
      "purchase_date": "2023-01-01",
      "total_amount": "500.00"
    },
    {
      "id": 2,
      "symbol": "AAPL",
      "quantity": 10,
      "purchase_price": "150.50",
      "purchase_date": "2023-01-05",
      "total_amount": "1505.00"
    }
  ],
  "total_portfolio_value": "2005.00"
}

Add a new stock to the portfolio

Endpoint: /api/portfolio/stocks/

Method: POST

Request Body (JSON):

{
  "stock_symbol": "GOOG",
  "quantity": 5,
  "purchase_price": 100.00
}

Retrieve, Update, or Delete a specific stock holding

Endpoint: /api/portfolio/stocks/<int:pk>/

Methods: GET, PUT, PATCH, DELETE

Description: The <int:pk> is the ID of the specific Holdings object you want to interact with.

## 3. Database Models
The project is built around four primary database models.

CustomUser: Extends Django's built-in AbstractUser.

Fields: email, username, date_of_birth, profile_photo.

Portfolio: Represents a user's stock portfolio.

Relationship: Has a one-to-one relationship with CustomUser.

Stock: Represents a unique stock symbol (e.g., 'AAPL'). This model is used to store and manage stock symbols across the application.

Holdings: A link between a Portfolio and a Stock, storing the number of units and purchase price.

Fields: portfolio, stock, quantity, purchase_price, purchase_date.

Uniqueness: It enforces a unique combination of portfolio and stock to prevent duplicate entries.

## 4. External API Usage
The project utilizes the Polygon.io API to fetch live stock prices. The get_live_stock_price function in services.py is responsible for this, contradicting the previous claim that no external APIs were used.

## 5. Django Admin
The Django admin interface is customized to improve management of user and portfolio data. The CustomUserAdmin class adds the custom fields (date_of_birth and profile_photo) to the user management forms.

## 6. Key Dependencies
This project relies on the following key Python libraries, which should be installed in your environment:

    Django

    djangorestframework

    djangofilters

    pillow

    django-taggit

    djangorestframework-authtoken