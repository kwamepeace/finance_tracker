This document provides a comprehensive overview of the Stock Portfolio Tracker, a secure, web-based application built with Django and Django REST Framework.

## 1. Project Overview
The application is designed to allow authenticated users to manage a personal stock portfolio. Upon registration, user creates a portfolio. The application handles the creation, retrieval, updating, and deletion of stock holdings, while also automatically calculating the total value of the portfolio. The project uses token-based authentication to secure user data.

## 2. API Endpoints
The API is built using Django REST Framework's ViewSets. All endpoints, except for registration and login, require an authentication token.

User Authentication
<Register a new user

Endpoint: /api/v1/auth/register/

Method: POST

Request Body (JSON):

{
  "email": "elvisofori011@gmail.com",
  "password": "Qwertyuiop193//",
  "password2": "Qwertyuiop193//",
  "username": "KusiEddys",
  "date_of_birth": "2003-05-03"
}

Success Response (201 Created):

Account successfully created👌
{
  "token": "a1b2c3d4e5f6...",
  "user_id": 1
}

<Log in an existing user

Endpoint: ttp://127.0.0.1:8000/api/v1/users/login/

Method: POST

Request Body (JSON):

{
  "email": "elvisofori8@gmail.com",
  "password": "Qwertyuiop123/"
}

Success Response (200 OK):

{
  "token": "a1b2c3d4e5f6..."
}

<Portfolio Management>
Authentication for these endpoints requires adding Authorization: Token <your_token> to the request headers.

<Create a new Portfolio

Endpoint: http://127.0.0.1:8000/api/v1/users/portfolio/

Method: POST

Description: Verifies an aunthenticated user's and create a new Portfolio.

Request Body (JSON):
{
  "name" : " house"
}

Success Response (HTTP 201 Created)

<Retrieve the user's portfolio

Endpoint: http://127.0.0.1:8000/api/v1/users/portfolio/

Method: GET

Description: Retrieves the authenticated user's portfolio, including all stock holdings and the total portfolio value.

Success Response (200 OK):

{
  "id": house,
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


## Add a New Stock to a Portfolio
This test case validates that an authenticated user can add a new stock to an existing portfolio they own.
You will need a valid authentication token and the name of the portfolio you wish to add the stock to. 
The stock symbol for Nvidia is NVDA.

Test URL: ttp://127.0.0.1:8000/api/v1/users/holdings/

Method: POST

Headers: Authorization: Token <your_token>

Request Body (JSON):

{
  "portfolio_name": "My First Portfolio",
  "symbol": "NVDA",
  "quantity": 200,
  "purchase_price": 1000.00
}

## Retrieve, Update, or Delete a Specific Stock Holding
These endpoints allow you to perform CRUD (Create, Read, Update, Delete) operations on a single stock holding 
within a user's portfolio. All of these operations require the unique id of the holding, which you can get 
from the response when you create a holding or by retrieving a list of all holdings.

Request Details
Test URL: api/holdings/<int:id>/

Headers: Authorization: Token <your_token>

<Retrieve a Specific Holding>
To retrieve the details of a single holding, use a GET request.

Method: GET

Example URL: api/holdings/1/ 

Expected Result: An HTTP 200 OK status with the holding's data in the response body.

Example Response:

JSON

{
  "id": 1,
  "symbol": "NVDA",
  "quantity": 2,
  "purchase_price": "1000.00",
  "purchase_date": "2025-09-07",
  "total_amount": "2000.00"
}

<Update a Holding>
To modify an existing holding, you can use either a PUT or PATCH request.

PUT (Full Update): This method requires all fields to be sent in the request body else any omitted field 
will be set to its default value or an error will be raised.

Method: PUT

Example URL: api/holdings/1/

Request Body:

JSON

{
  "portfolio_name": "house",
  "symbol": "NVDA",
  "quantity": 300,
  "purchase_price": 2050.50
}
Expected Result: An HTTP 200 OK status with the updated holding's data.

<PATCH (Partial Update)>: 
This method only requires the fields you want to change. This is often more convenient.

Method: PATCH

Example URL: api/holdings/1/

Request Body:

JSON

{
  "quantity": 350,
  "purchase_price": 3050.50
}
Expected Result: An HTTP 200 OK status with the updated holding's data.

<Delete a Holding>
To remove a stock from your portfolio, send a DELETE request.

Method: DELETE

Example URL: api/holdings/1/

Expected Result: An HTTP 204 No Content status code and an empty response body. This indicates a successful deletion.

## 3. Database Models
The project is built around four primary database models.

CustomUser: Extends Django's built-in AbstractUser.

Fields: email, username, date_of_birth, profile_photo.

Portfolio: Represents a user's stock portfolio.

Relationship: Has a mant-to-one relationship (foreign key) with CustomUser.

Stock: Represents a unique stock symbol (e.g., 'AAPL'). This model is used to store and manage stock symbols across 
the application.

Holdings: A link between a Portfolio and a Stock, storing the number of units and purchase price.

Fields: portfolio, stock, quantity, purchase_price, purchase_date.

Uniqueness: It enforces a unique combination of portfolio and stock to prevent duplicate entries.

## 4. External API Usage- Removed due to implementation issues
The project utilizes the Polygon.io API to fetch live stock prices. The get_live_stock_price function in services.py is responsible for this, contradicting the previous claim that no external APIs were used.

## 5. Django Admin --removed now to meet RESTFul framework
The Django admin interface is customized to improve management of user and portfolio data. The CustomUserAdmin class adds the custom fields (date_of_birth and profile_photo) to the user management forms.

## 6. Key Dependencies
This project relies on the following key Python libraries, which should be installed in your environment:

    Django

    djangorestframework

    djangofilters

    pillow

    django-taggit

    djangorestframework-authtoken